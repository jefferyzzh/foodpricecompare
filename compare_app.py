import streamlit as st
import pandas as pd
import os
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
    st.subheader("📁 所有项目")
    st.dataframe(projects, use_container_width=True)

    st.markdown("### ➕ 添加/修改项目")
    with st.form("add_project"):
        edit_mode = st.checkbox("修改已有项目")
        if edit_mode:
            project_to_edit = st.selectbox("选择要修改的项目", projects["项目名称"])
            project_row = projects[projects["项目名称"] == project_to_edit]
            new_name = st.text_input("项目名称", value=project_row["项目名称"].values[0])
            new_date = st.date_input("询价日期", value=pd.to_datetime(project_row["询价日期"].values[0]))
        else:
            new_name = st.text_input("项目名称")
            new_date = st.date_input("询价日期", value=date.today())
        
        submit = st.form_submit_button("✅ 保存项目")
        if submit and new_name:
            if edit_mode:
                idx = projects[projects["项目名称"] == project_to_edit].index[0]
                projects.at[idx, "项目名称"] = new_name
                projects.at[idx, "询价日期"] = new_date
            else:
                new_id = projects["项目ID"].max() + 1 if not projects.empty else 1
                new_row = pd.DataFrame([[new_id, new_name, new_date, str(date.today())]], columns=projects.columns)
                projects = pd.concat([projects, new_row], ignore_index=True)
            projects.to_csv(os.path.join(base_dir, "projects.csv"), index=False)
            st.rerun()

    st.markdown("### 🗑 删除项目")
    del_proj = st.selectbox("选择要删除的项目", projects["项目名称"])
    if st.button("删除选中的项目"):
        projects = projects[projects["项目名称"] != del_proj]
        projects.to_csv(os.path.join(base_dir, "projects.csv"), index=False)
        st.success(f"项目【{del_proj}】已删除")
        st.rerun()

# 商品管理
with tab2:
    st.subheader("📦 商品库")
    st.dataframe(products, use_container_width=True)

    st.markdown("### ➕ 添加/修改商品")
    with st.form("add_product"):
        edit_mode_prod = st.checkbox("修改已有商品")
        if edit_mode_prod:
            product_to_edit = st.selectbox("选择要修改的商品", products["品名"])
            prod_row = products[products["品名"] == product_to_edit]
            name = st.text_input("品名", value=prod_row["品名"].values[0])
            spec = st.text_input("规格", value=prod_row["规格"].values[0])
            unit = st.text_input("单位", value=prod_row["单位"].values[0])
            limit = st.number_input("限价", min_value=0.01, value=float(prod_row["限价"].values[0]))
            cat = st.selectbox("类别", ["蔬菜", "水果", "肉制品", "水产", "副食", "调料"], index=["蔬菜", "水果", "肉制品", "水产", "副食", "调料"].index(prod_row["类别"].values[0]))
        else:
            name = st.text_input("品名")
            spec = st.text_input("规格")
            unit = st.text_input("单位")
            limit = st.number_input("限价", min_value=0.01)
            cat = st.selectbox("类别", ["蔬菜", "水果", "肉制品", "水产", "副食", "调料"])

        submit_prod = st.form_submit_button("✅ 保存商品")
        if submit_prod and name:
            if edit_mode_prod:
                idx = products[products["品名"] == product_to_edit].index[0]
                products.at[idx, "品名"] = name
                products.at[idx, "规格"] = spec
                products.at[idx, "单位"] = unit
                products.at[idx, "限价"] = limit
                products.at[idx, "类别"] = cat
            else:
                new_id = products["商品ID"].max() + 1 if not products.empty else 1
                new_row = pd.DataFrame([[new_id, name, spec, unit, limit, cat]], columns=products.columns)
                products = pd.concat([products, new_row], ignore_index=True)
            products.to_csv(os.path.join(base_dir, "products.csv"), index=False)
            st.rerun()

    st.markdown("### 🗑 删除商品")
    del_prod = st.selectbox("选择要删除的商品", products["品名"])
    if st.button("删除选中的商品"):
        products = products[products["品名"] != del_prod]
        products.to_csv(os.path.join(base_dir, "products.csv"), index=False)
        st.success(f"商品【{del_prod}】已删除")
        st.rerun()

# 商品报价
with tab3:
    st.subheader("🧾 项目商品报价")
    if projects.empty or products.empty:
        st.info("请先录入项目和商品")
    else:
        pid = st.selectbox("选择项目", projects["项目名称"])
        proj_id = projects[projects["项目名称"] == pid]["项目ID"].values[0]
        st.markdown("### 📄 当前项目商品报价：")
        q_this = quotes[quotes["项目ID"] == proj_id].merge(products, on="商品ID", how="left")
        st.dataframe(q_this[["品名", "规格", "单位", "类别", "价格"]], use_container_width=True)

        with st.form("add_quote"):
            pname = st.selectbox("选择商品", products["品名"])
            prod_id = products[products["品名"] == pname]["商品ID"].values[0]
            price = st.number_input("本次报价", min_value=0.01)
            ok = st.form_submit_button("✅ 添加报价")
            if ok:
                new_row = pd.DataFrame([[proj_id, prod_id, price]], columns=quotes.columns)
                quotes = pd.concat([quotes, new_row], ignore_index=True)
                quotes.to_csv(os.path.join(base_dir, "quotes.csv"), index=False)
                st.rerun()

# 项目比价分析
with tab4:
    st.subheader("📊 项目间比价分析")
    if len(projects) < 2:
        st.info("至少需要两个项目进行比价")
    else:
        col1, col2 = st.columns(2)
        p1 = col1.selectbox("项目 A", projects["项目名称"], index=0)
        p2 = col2.selectbox("项目 B", projects["项目名称"], index=1)
        id1 = projects[projects["项目名称"] == p1]["项目ID"].values[0]
        id2 = projects[projects["项目名称"] == p2]["项目ID"].values[0]
        q1 = quotes[quotes["项目ID"] == id1].set_index("商品ID")["价格"]
        q2 = quotes[quotes["项目ID"] == id2].set_index("商品ID")["价格"]
        all_ids = sorted(set(q1.index) | set(q2.index))

        rows = []
        for sid in all_ids:
            name = products[products["商品ID"] == sid]["品名"].values[0]
            cat = products[products["商品ID"] == sid]["类别"].values[0]
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
            rows.append([name, cat, p_old, p_new, diff, pct, status])

        df = pd.DataFrame(rows, columns=["品名", "类别", "项目A", "项目B", "涨跌额", "涨跌幅%", "状态"])

        def color_status(val):
            if val == "↑":
                return "color:red;font-weight:bold"
            elif val == "↓":
                return "color:green;font-weight:bold"
            else:
                return "color:gray;font-weight:bold"

        st.dataframe(df.style.applymap(color_status, subset=["状态"]), use_container_width=True)