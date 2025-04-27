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
    categories = pd.read_csv(os.path.join(base_dir, "categories.csv"))
except Exception as e:
    st.error(f"❌ 数据读取失败：{e}")
    st.stop()

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📁 项目管理", "📦 商品管理", "🏷️ 商品类别管理", "🧾 报价管理", "📊 比价分析"])
# 项目管理
with tab1:
    st.subheader("📁 项目管理")
    if st.button("➕ 新增项目"):
        with st.form("add_project_form", clear_on_submit=True):
            pname = st.text_input("项目名称")
            qdate = st.date_input("询价日期", value=date.today())
            submitted = st.form_submit_button("✅ 保存项目")
            if submitted:
                new_id = projects["项目ID"].max() + 1 if not projects.empty else 1
                new_row = pd.DataFrame([[new_id, pname, qdate, str(date.today())]], columns=projects.columns)
                projects = pd.concat([projects, new_row], ignore_index=True)
                projects.to_csv(os.path.join(base_dir, "projects.csv"), index=False)
                projects = pd.read_csv(os.path.join(base_dir, "projects.csv"))
                st.success("✅ 项目添加成功！")
                st.rerun()

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
        st.success("✅ 项目保存成功")
        st.rerun()

    if st.button("🗑 批量删除选中项目"):
        if selected_rows is not None and len(selected_rows) > 0:
            try:
                to_delete_ids = [r["项目ID"] for r in selected_rows if isinstance(r, dict) and "项目ID" in r]
                if to_delete_ids:
                    updated_projects = updated_projects[~updated_projects["项目ID"].isin(to_delete_ids)]
                    updated_projects.to_csv(os.path.join(base_dir, "projects.csv"), index=False)
                    st.success("✅ 已删除选中项目")
                    st.rerun()
                else:
                    st.warning("⚠️ 没有正确选中项目，请重新选择")
            except Exception as e:
                st.error(f"❌ 删除时出错：{e}")
        else:
            st.warning("⚠️ 请选择要删除的项目！")

# 商品管理
with tab2:
    st.subheader("📦 商品管理")
    if st.button("➕ 新增商品"):
        with st.form("add_product_form", clear_on_submit=True):
            pname = st.text_input("商品名称")
            spec = st.text_input("规格")
            unit = st.text_input("单位")
            limit = st.number_input("限价", min_value=0.01, format="%.2f")
            cat = st.selectbox("类别", categories["类别名称"])
            submitted = st.form_submit_button("✅ 保存商品")
            if submitted:
                new_id = products["商品ID"].max() + 1 if not products.empty else 1
                new_row = pd.DataFrame([[new_id, pname, spec, unit, limit, cat]], columns=products.columns)
                products = pd.concat([products, new_row], ignore_index=True)
                products.to_csv(os.path.join(base_dir, "products.csv"), index=False)
                products = pd.read_csv(os.path.join(base_dir, "products.csv"))
                st.success("✅ 商品添加成功！")
                st.rerun()

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
        st.success("✅ 商品保存成功")
        st.rerun()

    if st.button("🗑 批量删除选中商品"):
        if selected_rows is not None and len(selected_rows) > 0:
            try:
                to_delete_ids = [r["商品ID"] for r in selected_rows if isinstance(r, dict) and "商品ID" in r]
                if to_delete_ids:
                    updated_products = updated_products[~updated_products["商品ID"].isin(to_delete_ids)]
                    updated_products.to_csv(os.path.join(base_dir, "products.csv"), index=False)
                    st.success("✅ 已删除选中商品")
                    st.rerun()
                else:
                    st.warning("⚠️ 没有正确选中商品，请重新选择")
            except Exception as e:
                st.error(f"❌ 删除时出错：{e}")
        else:
            st.warning("⚠️ 请选择要删除的商品！")

# 商品类别管理
with tab3:
    st.subheader("🏷️ 商品类别管理")
    if st.button("➕ 新增类别"):
        with st.form("add_category_form", clear_on_submit=True):
            cname = st.text_input("类别名称")
            submitted = st.form_submit_button("✅ 保存类别")
            if submitted:
                new_id = categories["类别ID"].max() + 1 if not categories.empty else 1
                new_row = pd.DataFrame([[new_id, cname]], columns=categories.columns)
                categories = pd.concat([categories, new_row], ignore_index=True)
                categories.to_csv(os.path.join(base_dir, "categories.csv"), index=False)
                categories = pd.read_csv(os.path.join(base_dir, "categories.csv"))
                st.success("✅ 类别添加成功！")
                st.rerun()

    gb = GridOptionsBuilder.from_dataframe(categories)
    gb.configure_selection('multiple', use_checkbox=True)
    gb.configure_pagination()
    gb.configure_default_column(editable=True, groupable=True)
    grid_options = gb.build()

    grid_response = AgGrid(
        categories,
        gridOptions=grid_options,
        height=400,
        width='100%',
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        fit_columns_on_grid_load=True,
        reload_data=True,
    )

    updated_categories = grid_response['data']
    selected_rows = grid_response['selected_rows']

    if st.button("💾 保存类别修改"):
        updated_categories.to_csv(os.path.join(base_dir, "categories.csv"), index=False)
        st.success("✅ 类别保存成功")
        st.rerun()

    if st.button("🗑 批量删除选中类别"):
        if selected_rows is not None and len(selected_rows) > 0:
            try:
                to_delete_ids = [r["类别ID"] for r in selected_rows if isinstance(r, dict) and "类别ID" in r]
                if to_delete_ids:
                    updated_categories = updated_categories[~updated_categories["类别ID"].isin(to_delete_ids)]
                    updated_categories.to_csv(os.path.join(base_dir, "categories.csv"), index=False)
                    st.success("✅ 已删除选中类别")
                    st.rerun()
                else:
                    st.warning("⚠️ 没有正确选中类别，请重新选择")
            except Exception as e:
                st.error(f"❌ 删除时出错：{e}")
        else:
            st.warning("⚠️ 请选择要删除的类别！")
 # 报价管理
with tab4:
    st.subheader("🧾 报价管理")
    if projects.empty or products.empty:
        st.info("请先录入项目和商品")
    else:
        col1, col2 = st.columns(2)
        pid = col1.selectbox("选择项目", projects["项目名称"])
        proj_id = projects[projects["项目名称"] == pid]["项目ID"].values[0]
        selected_cat = col2.selectbox("筛选类别", ["全部"] + list(categories["类别名称"]))

        filtered_products = products
        if selected_cat != "全部":
            filtered_products = products[products["类别"] == selected_cat]

        pname = st.selectbox("选择商品", filtered_products["品名"])
        prod_id = filtered_products[filtered_products["品名"] == pname]["商品ID"].values[0]
        limit_price = filtered_products[filtered_products["品名"] == pname]["限价"].values[0]

        price = st.number_input("本次报价（元）", min_value=0.01, format="%.2f")

        if st.button("✅ 添加报价"):
            new_row = pd.DataFrame([[proj_id, prod_id, price]], columns=quotes.columns)
            quotes = pd.concat([quotes, new_row], ignore_index=True)
            quotes.to_csv(os.path.join(base_dir, "quotes.csv"), index=False)
            st.success("✅ 报价添加成功！")
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

# 项目比价分析
with tab5:
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
            p_old = q1.get(sid)
            p_new = q2.get(sid)

            # 防止 Series 错误，强制取第一个值
            if isinstance(p_old, pd.Series):
                p_old = p_old.values[0]
            if isinstance(p_new, pd.Series):
                p_new = p_new.values[0]

            # 开始判断
            if pd.notna(p_old) and pd.notna(p_new):
                status = "↑" if p_new > p_old else "↓" if p_new < p_old else "→"
            elif pd.isna(p_old) and pd.notna(p_new):
                status = "新增"
            elif pd.notna(p_old) and pd.isna(p_new):
                status = "未报价"
            else:
                status = "无比较"

            diff = (p_new - p_old) if pd.notna(p_old) and pd.notna(p_new) else None
            pct = (diff / p_old * 100) if diff is not None and p_old else None
            rows.append([name, p_old, p_new, diff, pct, status])

        df = pd.DataFrame(rows, columns=["品名", "项目A", "项目B", "涨跌额", "涨跌幅%", "状态"])

        def color_arrow(val):
            if val == "↑":
                return "color:red; font-weight:bold"
            elif val == "↓":
                return "color:green; font-weight:bold"
            else:
                return "color:gray; font-weight:bold"

        st.dataframe(df.style.applymap(color_arrow, subset=["状态"]), use_container_width=True)

        st.markdown("### 📈 商品价格走势")
        product_choice = st.selectbox("选择商品查看价格走势", products["品名"], key="chart_prod")
        prod_id_choice = products[products["品名"] == product_choice]["商品ID"].values[0]

        trend_data = quotes[quotes["商品ID"] == prod_id_choice].merge(projects, on="项目ID")
        if not trend_data.empty:
            trend_data = trend_data.sort_values("询价日期")
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.plot(trend_data["询价日期"], trend_data["价格"], marker='o')
            ax.set_xlabel("询价日期")
            ax.set_ylabel("价格")
            ax.set_title(f"{product_choice} 价格走势")
            plt.xticks(rotation=45)
            st.pyplot(fig)