import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode
from datetime import date

st.set_page_config(page_title="原材料比价系统", layout="wide")
st.title("🔐 原材料比价系统")
password = st.text_input("请输入访问密码", type="password")
if password != "abc123":
    st.warning("密码错误，或尚未输入密码")
    st.stop()
st.success("✅ 登录成功！欢迎使用原材料比价系统")

base_dir = os.path.dirname(os.path.abspath(__file__))
try:
    projects = pd.read_csv(os.path.join(base_dir, "projects.csv"))
    products = pd.read_csv(os.path.join(base_dir, "products.csv"))
    quotes = pd.read_csv(os.path.join(base_dir, "quotes.csv"))
except Exception as e:
    st.error(f"❌ 数据读取失败：{e}")
    st.stop()

tab1, tab2, tab3, tab4 = st.tabs(["📁 项目管理", "📦 商品管理", "🧾 商品报价", "📊 比价分析"])
# 项目管理
with tab1:
    st.subheader("📁 项目管理")
    gb = GridOptionsBuilder.from_dataframe(projects)
    gb.configure_selection('multiple', use_checkbox=True)
    gb.configure_pagination()
    gb.configure_default_column(editable=True, groupable=True)
    grid_options = gb.build()

    grid_response = AgGrid(
        projects,
        gridOptions=grid_options,
        height=400,
        width='100%',
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        fit_columns_on_grid_load=True,
        reload_data=True,
    )

    updated_projects = grid_response['data']
    selected_rows = grid_response['selected_rows']

    if st.button("💾 保存修改项目"):
        updated_projects.to_csv(os.path.join(base_dir, "projects.csv"), index=False)
        st.success("项目保存成功")
        st.rerun()

    if st.button("🗑 批量删除选中项目"):
        if selected_rows is not None and len(selected_rows) > 0:
            to_delete_ids = [r['项目ID'] for r in selected_rows if isinstance(r, dict)]
            updated_projects = updated_projects[~updated_projects['项目ID'].isin(to_delete_ids)]
            updated_projects.to_csv(os.path.join(base_dir, "projects.csv"), index=False)
            st.success("已删除选中项目")
            st.rerun()

    if st.button("📄 导出项目CSV"):
        updated_projects.to_csv("导出项目列表.csv", index=False)
        with open("导出项目列表.csv", "rb") as f:
            st.download_button("点击下载项目CSV", f, file_name="projects_export.csv")

# 商品管理
with tab2:
    st.subheader("📦 商品管理")
    gb = GridOptionsBuilder.from_dataframe(products)
    gb.configure_selection('multiple', use_checkbox=True)
    gb.configure_pagination()
    gb.configure_default_column(editable=True, groupable=True)
    grid_options = gb.build()

    grid_response = AgGrid(
        products,
        gridOptions=grid_options,
        height=400,
        width='100%',
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        fit_columns_on_grid_load=True,
        reload_data=True,
    )

    updated_products = grid_response['data']
    selected_rows = grid_response['selected_rows']

    if st.button("💾 保存商品修改"):
        updated_products.to_csv(os.path.join(base_dir, "products.csv"), index=False)
        st.success("商品保存成功")
        st.rerun()

    if st.button("🗑 批量删除选中商品"):
        if selected_rows is not None and len(selected_rows) > 0:
            to_delete_ids = [r['商品ID'] for r in selected_rows if isinstance(r, dict)]
            updated_products = updated_products[~updated_products['商品ID'].isin(to_delete_ids)]
            updated_products.to_csv(os.path.join(base_dir, "products.csv"), index=False)
            st.success("已删除选中商品")
            st.rerun()

# 商品报价
with tab3:
    st.subheader("🧾 商品报价录入")
    if projects.empty or products.empty:
        st.info("请先录入项目和商品")
    else:
        pid = st.selectbox("选择项目", projects["项目名称"])
        proj_id = projects[projects["项目名称"] == pid]["项目ID"].values[0]

        pname = st.selectbox("选择商品", products["品名"])
        prod_id = products[products["品名"] == pname]["商品ID"].values[0]

        limit_price = products[products["品名"] == pname]["限价"].values[0]

        price = st.number_input("本次报价", min_value=0.01)

        if st.button("✅ 添加报价"):
            new_row = pd.DataFrame([[proj_id, prod_id, price]], columns=quotes.columns)
            quotes = pd.concat([quotes, new_row], ignore_index=True)
            quotes.to_csv(os.path.join(base_dir, "quotes.csv"), index=False)
            st.success("报价添加成功")
            st.rerun()

        st.markdown("### 📈 当前项目商品报价")
        q_this = quotes[quotes["项目ID"] == proj_id].merge(products, on="商品ID", how="left")
        if not q_this.empty:
            def highlight_price(val, limit=limit_price):
                try:
                    return "color: red; font-weight: bold" if float(val) > float(limit) else ""
                except:
                    return ""
            styled = q_this.style.applymap(lambda v: highlight_price(v) if isinstance(v, (int, float)) else "", subset=["价格"])
            st.dataframe(styled, use_container_width=True)

# 比价分析
with tab4:
    st.subheader("📊 项目比价分析")
    if len(projects) < 2:
        st.info("至少需要两个项目进行比价")
    else:
        col1, col2 = st.columns(2)
        p1 = col1.selectbox("项目 A", projects["项目名称"], key="p1")
        p2 = col2.selectbox("项目 B", projects["项目名称"], key="p2")
        id1 = projects[projects["项目名称"] == p1]["项目ID"].values[0]
        id2 = projects[projects["项目名称"] == p2]["项目ID"].values[0]
        q1 = quotes[quotes["项目ID"] == id1].set_index("商品ID")["价格"]
        q2 = quotes[quotes["项目ID"] == id2].set_index("商品ID")["价格"]

        all_ids = sorted(set(q1.index) | set(q2.index))
        rows = []
        for sid in all_ids:
            name = products[products["商品ID"] == sid]["品名"].values[0]
            p_old = q1.get(sid, None)
            p_new = q2.get(sid, None)
            if p_old is None:
                status = "新增"
            elif p_new is None:
                status = "未报价"
            else:
                status = "↑" if p_new > p_old else "↓" if p_new < p_old else "→"
            diff = (p_new - p_old) if p_old and p_new else None
            pct = (diff / p_old * 100) if diff and p_old else None
            rows.append([name, p_old, p_new, diff, pct, status])

        df = pd.DataFrame(rows, columns=["品名", "项目A", "项目B", "涨跌额", "涨跌幅%", "状态"])
        st.dataframe(df, use_container_width=True)

        # 绘制价格走势
        st.markdown("### 📈 商品价格走势")
        product_choice = st.selectbox("选择商品查看价格走势", products["品名"], key="chart_prod")
        prod_id_choice = products[products["品名"] == product_choice]["商品ID"].values[0]

        trend_data = quotes[quotes["商品ID"] == prod_id_choice].merge(projects, on="项目ID")
        if not trend_data.empty:
            trend_data = trend_data.sort_values("询价日期")
            fig, ax = plt.subplots()
            ax.plot(trend_data["询价日期"], trend_data["价格"], marker='o')
            ax.set_xlabel("询价日期")
            ax.set_ylabel("价格")
            ax.set_title(f"{product_choice} 价格走势")
            st.pyplot(fig)