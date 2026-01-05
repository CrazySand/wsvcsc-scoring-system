import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
from tabulate import tabulate

# ------------------------------------------ 页面配置 ----------------------------------------- #

# 设置页面配置
st.set_page_config(
    page_title="职业技能大赛成绩统计系统",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'KaiTi', 'FangSong', 'STSong', 'Arial Unicode MS', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
plt.rcParams['font.family'] = 'sans-serif'

# 自定义 CSS 样式，根据不同的图标设置不同的背景颜色
custom_css = """\
<style>
    .header {
        text-align: center;
        font-size: 2.5rem;
        color: #1a3d7c;
        padding: 1rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #e4edf9 100%);
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    .section {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #f8f9fa;
        border-left: 4px solid #1a3d7c;
        padding: 1rem;
        border-radius: 5px;
    }
    .stButton>button {
        background-color: #1a3d7c;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #0d2b5c;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .stDownloadButton>button {
        background-color: #1a3d7c;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        transition: all 0.3s;
    }
    .stDownloadButton>button:hover {
        background-color: #0d2b5c;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .footer {
        text-align: center;
        padding: 1rem;
        color: #6c757d;
        font-size: 0.9rem;
    }
    
    /* 调整文件上传区域的大小 */
    .css-1cpxqw2[data-testid="stFileUploader"] {
        width: 100%;
        padding: 0.5rem;
    }
    
    /* 调整上传文件的按钮大小 */
    button[data-testid="stFileUploaderUploadButton"] {
        font-size: 0.8rem !important;
        padding: 0.2rem 0.5rem !important;
        height: auto !important;
    }
    
    /* 调整拖放区域的高度 */
    .css-1cpxqw2[data-testid="stFileUploader"] > div:first-child {
        min-height: 80px !important;
    }
    
    /* 修改按钮文字为中文 */
    button[data-testid="stFileUploaderUploadButton"]::before {
        content: "浏览文件";
        visibility: visible;
        display: block;
    }
    
    button[data-testid="stFileUploaderUploadButton"] span {
        visibility: hidden;
        position: relative;
    }
    
    button[data-testid="stFileUploaderUploadButton"] span::after {
        visibility: visible;
        position: absolute;
        top: 0;
        left: 0;
        content: "";
    }
</style>\
"""
# 注入自定义 CSS 样式
st.markdown(custom_css, unsafe_allow_html=True)

# ------------------------------------------ Logo 标题 ----------------------------------------- #

# 添加学校 logo 居中显示
school_logo = ".\\school.png"
col1, col2 = st.columns([2, 15])
with col2:
    st.image(school_logo, width=800)

# 页面标题
st.markdown(
    '<div class="header">2025年世界职业院校技能大赛广东赛区<br>"人工智能赛道" 遴选赛成绩计分系统</div>',
    unsafe_allow_html=True,
)

# ------------------------------------------ 侧边栏 -------------------------------------------- #

# 使用 Streamlit 的 sidebar 上下文管理器，将后续内容显示在侧边栏中
with st.sidebar:
    # 在侧边栏中显示一个标题为 "系统设置" 的标题
    st.header("系统设置")
    # 创建一个滑动条组件，让用户可以调整最小标准差保护值
    # min_std 对 st.slider 的返回值进行了类型注释，指定其类型为 float
    min_std = st.slider(
        # 滑动条的标签，显示在滑动条上方
        "最小标准差保护值",
        # 滑动条的最小值
        1.0,
        # 滑动条的最大值
        20.0,
        # 滑动条的初始值
        5.0,
        # 滑动条每次调整的步长
        0.5,
        # 鼠标悬停在滑动条上时显示的帮助信息
        help="防止小组标准差过小导致分数异常波动",
    )
    # 创建一个复选框组件，用户可以选择是否显示分数分布图
    # 初始状态为选中（True）
    show_dist = st.checkbox("显示分数分布图", True)
    # 在侧边栏中添加一条分隔线，用于区分不同内容区域
    st.divider()
    # 使用 Markdown 语法在侧边栏中显示加粗的 "使用说明" 文本
    st.markdown("**使用说明**")
    # 在侧边栏中显示一个信息提示框，内容为操作步骤
    st.info("1. 在下方输入或上传参赛队伍成绩\n2. 点击 '计算最终成绩' 按钮\n3. 查看结果并导出报表")
    # 在侧边栏中再添加一条分隔线
    st.divider()

# ------------------------------------------ 成绩录入 ------------------------------------------ #

# 初始化 session_state.team_data 为 DataFrame，用于存储队伍数据
st.session_state.team_data = pd.DataFrame(columns=["组别", "工位", "队伍名称", "原始分"])

# 将多个 Streamlit 组件组合起来，这些组件会按顺序垂直排列在容器内
with st.container():
    st.markdown("### 参赛队伍成绩录入")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # 手动输入表格
        edited_df = st.data_editor(
            st.session_state.team_data,
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True,  # 隐藏索引列
            column_config={
                "组别": st.column_config.SelectboxColumn(
                    "组别",
                    options=["高职(专科)", "高职(本科)", "高中", "中职", "普通本科"],
                    required=True,
                    width="medium"
                ),
                "工位": st.column_config.SelectboxColumn(
                    "工位",
                    options=["工位1", "工位2", "工位3", "工位4", "工位5", "工位6", "工位7"],
                    required=True,
                    width="small"
                ),
                "队伍名称": st.column_config.TextColumn(
                    "队伍名称", width="medium", required=True
                ),
                "原始分": st.column_config.NumberColumn(
                    "原始分",
                    min_value=0,
                    max_value=100,
                    step=0.1,
                    format="%.1f",
                    required=True,
                    width="small"
                ),
            },
            key="team_data_editor",  # 添加唯一键以保持状态一致
        )
        # 更新 session_state 中的数据
        st.session_state.team_data = edited_df.reset_index(drop=True)  # 重置索引并丢弃原索引
        
        print('\n\n')
        print(tabulate(st.session_state.team_data, headers="keys", tablefmt="pretty"))
        print('最小标准差:', min_std)

    with col2:
        # 文件上传功能，将文件上传组件放置在 col2 列中
        uploaded_file = st.file_uploader(
            # 文件上传组件的标签，显示在组件上方
            "上传成绩文件",
            # 允许上传的文件类型，支持 Excel 和 CSV 格式
            type=["xlsx", "csv"],
            # 鼠标悬停在组件上时显示的帮助信息，提示文件格式和必要列
            help="支持Excel或CSV格式，需包含'组别'、'工位'、'队伍名称'和'原始分'列",
        )
        # 检查用户是否上传了文件
        if uploaded_file:
            try:
                # 判断上传文件是否为 CSV 格式
                if uploaded_file.name.endswith(".csv"):
                    # 若为 CSV 格式，使用 pandas 的 read_csv 函数读取文件
                    df = pd.read_csv(uploaded_file)
                else:
                    # 若为非 CSV 格式（即 Excel 格式），使用 pandas 的 read_excel 函数读取文件
                    df = pd.read_excel(uploaded_file)

                # 定义文件中必须包含的列名
                required_columns = ["组别", "工位", "队伍名称", "原始分"]
                
                # 检查 DataFrame 的列是否包含所有必要列
                if all(col in df.columns for col in required_columns):
                    # 若包含所有必要列，从 DataFrame 中提取这些列并复制一份
                    df = df[required_columns].copy()
                    
                    # 生成有效的工位列表，包含 "工位1" 到 "工位7"
                    valid_stations = [f"工位{i}" for i in range(1, 8)]
                    # 检查 DataFrame 中的 "工位" 列是否存在无效值
                    if not df["工位"].isin(valid_stations).all():
                        # 找出所有无效的工位值
                        invalid_stations = df[~df["工位"].isin(valid_stations)]["工位"].unique()
                        # 使用 Streamlit 显示警告信息，提示用户存在无效的工位值
                        st.toast("该文件包含无效的工位值，请检查并修正后重新上传。", icon="⚠️")
                    
                    # 按队伍名称分组，统计每个队伍出现的工位数
                    team_counts = df.groupby("队伍名称")["工位"].count()
                    # 找出在多个工位出现的队伍名称
                    duplicate_teams = team_counts[team_counts > 1].index.tolist()
                    
                    # 若存在在多个工位出现的队伍
                    if duplicate_teams:
                        # 使用 Streamlit 显示警告信息，提示用户哪些队伍在多个工位出现，并说明处理方式
                        st.toast(f"以下队伍在多个工位出现: {', '.join(duplicate_teams)}。系统将只保留每个队伍的第一条记录。", icon="⚠️")
                        # 去除每个队伍的重复记录，只保留第一条记录
                        df = df.drop_duplicates(subset=["队伍名称"], keep="first")
                    
                    # 将处理后的 DataFrame 存入 session_state 中
                    st.session_state.team_data = df.reset_index(drop=True)  # 重置索引并丢弃原索引
                    st.toast(f"成功导入 {len(df)} 条记录", icon="✅")

                    print("文件上传更新后的数据：")
                    print(tabulate(st.session_state.team_data, headers="keys", tablefmt="pretty"))
                else:
                    # 找出文件中缺失的必要列
                    missing_cols = [col for col in required_columns if col not in df.columns]
                    st.toast(f"文件缺少必要列: {', '.join(missing_cols)}", icon="⚠️")
            except Exception as e:
                # 若在文件处理过程中出现异常，使用 Streamlit 显示错误信息，提示用户具体的错误内容
                st.toast(f"文件处理出错: {e}", icon="❌")

# ------------------------------------------ 成绩计算 ------------------------------------------ #

def normalize_score(raw_score, group_avg, group_std, min_std):
    """标准分转换公式，带安全处理"""
    print('最小标准差:', min_std)
    # 如果标准差过小或为零，使用最小标准差值
    if group_std < min_std or np.isclose(group_std, 0):
        effective_std = min_std
    else:
        effective_std = group_std
    
    # 如果只有一个分数，返回70分(基准分)
    if np.isclose(group_std, 0):
        return 70.0
        
    score = 70 + 10 * (raw_score - group_avg) / effective_std
    return max(0, min(100, score))  # 限制在0-100区间

with st.container():
    col1, col2 = st.columns([3, 1])
    with col1:
        calculate_btn = st.button("计算最终成绩", type="primary", use_container_width=True)

    # 计算逻辑
    if calculate_btn:
        if len(st.session_state.team_data) < 2:
            st.toast("至少需要2支队伍才能进行计算！", icon="❌")
            st.stop()

        # 创建一个原始数据的副本进行计算
        raw_data = st.session_state.team_data.copy()
        
        # 重命名原始分为原始平均分（因为每队只有一个工位，所以原始分就是原始平均分）
        raw_data = raw_data.rename(columns={"原始分": "原始平均分"})
        
        # 以队伍为单位进行计算
        st.session_state.result_data = raw_data.copy()
        
        # 创建"工位+组别"的联合计分空间
        raw_data['计分空间'] = raw_data['工位'] + '-' + raw_data['组别']
        st.session_state.result_data['计分空间'] = st.session_state.result_data['工位'] + '-' + st.session_state.result_data['组别']
        
        # 初始化结果存储
        st.session_state.space_stats = {}
        # 获取所有计分空间
        all_spaces = st.session_state.result_data["计分空间"].unique()
        
        for space in all_spaces:
            # 获取当前计分空间的数据
            space_df = st.session_state.result_data[st.session_state.result_data["计分空间"] == space]
            
            # 从计分空间名称中提取工位和组别信息
            space_parts = space.split('-')
            station = space_parts[0]
            group = space_parts[1] if len(space_parts) > 1 else "未知组别"
            
            # 检查计分空间内队伍数量
            if len(space_df) <= 1:
                # 计算统计指标
                raw_scores = space_df["原始平均分"].values
                space_avg = np.mean(raw_scores)
                
                # 如果计分空间内只有一支队伍，设置标准分为70分(基准分)
                st.session_state.space_stats[space] = {
                    "工位": station,
                    "组别": group,
                    "队伍数量": len(space_df),
                    "平均分": space_avg,
                    "标准差": 0.0,
                    "最高分": raw_scores[0] if len(raw_scores) > 0 else 0,
                    "最低分": raw_scores[0] if len(raw_scores) > 0 else 0,
                }
                
                # 应用固定分数
                mask = st.session_state.result_data["计分空间"] == space
                st.session_state.result_data.loc[mask, "最终成绩"] = 70.0
                
                # 添加警告信息
                st.toast(f"警告: '{space}' (工位: {station}, 组别: {group}) 内只有一支队伍，无法进行标准分转换，已设置为基准分70分。", icon="⚠️")
            else:
                # 计算统计指标
                raw_scores = space_df["原始平均分"].values
                space_avg = np.mean(raw_scores)
                space_std = np.std(raw_scores, ddof=1)  # 样本标准差
                
                # 存储计分空间统计信息
                st.session_state.space_stats[space] = {
                    "工位": station,
                    "组别": group,
                    "队伍数量": len(space_df),
                    "平均分": space_avg,
                    "标准差": space_std,
                    "最高分": np.max(raw_scores) if len(raw_scores) > 0 else 0,
                    "最低分": np.min(raw_scores) if len(raw_scores) > 0 else 0,
                }
                
                # 应用标准分转换
                mask = st.session_state.result_data["计分空间"] == space
                st.session_state.result_data.loc[mask, "最终成绩"] = (
                    space_df["原始平均分"]
                    .apply(lambda x: normalize_score(x, space_avg, space_std, min_std))
                    .round(1)
                    .values
                )
        
        # 在各个维度单独排名
        st.session_state.result_data["组内排名"] = 0
        st.session_state.result_data["工位内排名"] = 0
        st.session_state.result_data["计分空间内排名"] = 0
        
        # 首先按组别排名
        all_groups = st.session_state.result_data["组别"].unique()
        for group in all_groups:
            # 获取当前组的索引
            group_idx = st.session_state.result_data[st.session_state.result_data["组别"] == group].index
            
            # 在组内排名
            st.session_state.result_data.loc[group_idx, "组内排名"] = (
                st.session_state.result_data.loc[group_idx, "最终成绩"]
                .rank(ascending=False, method="min")
                .astype(int)
                .values
            )
        
        # 然后按工位排名
        all_stations = st.session_state.result_data["工位"].unique()
        for station in all_stations:
            # 获取当前工位的索引
            station_idx = st.session_state.result_data[st.session_state.result_data["工位"] == station].index
            
            # 在工位内排名
            st.session_state.result_data.loc[station_idx, "工位内排名"] = (
                st.session_state.result_data.loc[station_idx, "最终成绩"]
                .rank(ascending=False, method="min")
                .astype(int)
                .values
            )
        
        # 最后按计分空间排名
        for space in all_spaces:
            # 获取当前计分空间的索引
            space_idx = st.session_state.result_data[st.session_state.result_data["计分空间"] == space].index
            
            # 在计分空间内排名
            st.session_state.result_data.loc[space_idx, "计分空间内排名"] = (
                st.session_state.result_data.loc[space_idx, "最终成绩"]
                .rank(ascending=False, method="min")
                .astype(int)
                .values
            )
        
        # 排序：先按计分空间，再按计分空间内排名
        st.session_state.result_data = st.session_state.result_data.sort_values(
            by=["计分空间", "计分空间内排名"]
        )
        
        # 计算总体统计数据
        total_raw_scores = st.session_state.result_data["原始平均分"].values
        st.session_state.total_stats = {
            "队伍数量": len(st.session_state.result_data),
            "平均分": np.mean(total_raw_scores),
            "标准差": np.std(total_raw_scores, ddof=1),
            "最高分": np.max(total_raw_scores),
            "最低分": np.min(total_raw_scores),
        }

    # 显示结果
    if "result_data" in st.session_state and "最终成绩" in st.session_state.result_data.columns:
        st.divider()

        # 总体统计指标卡片
        st.markdown("### 总体统计概览")
        cols = st.columns(4)
        total_stats = st.session_state.total_stats
        cols[0].metric("参赛队伍", f"{total_stats['队伍数量']}支")
        cols[1].metric("总平均分", f"{total_stats['平均分']:.1f}")
        cols[2].metric("总标准差", f"{total_stats['标准差']:.1f}")
        cols[3].metric("分数范围", f"{total_stats['最低分']:.1f}-{total_stats['最高分']:.1f}")

        # 分组统计
        st.markdown("### 组别统计")
        # 获取所有组别
        all_groups = sorted(st.session_state.result_data["组别"].unique())
        group_cols = st.columns(len(all_groups))
        
        for i, group in enumerate(all_groups):
            with group_cols[i]:
                st.markdown(f"#### {group}")
                group_df = st.session_state.result_data[st.session_state.result_data["组别"] == group]
                team_count = len(group_df)
                avg_score = group_df["原始平均分"].mean()
                std_score = group_df["原始平均分"].std(ddof=1) if len(group_df) > 1 else 0.0
                min_score = group_df["原始平均分"].min() if not group_df.empty else 0.0
                max_score = group_df["原始平均分"].max() if not group_df.empty else 0.0
                
                st.metric("队伍数量", f"{team_count}支")
                st.metric("平均分", f"{avg_score:.1f}")
                st.metric("标准差", f"{std_score:.1f}")
                st.metric("分数范围", f"{min_score:.1f}-{max_score:.1f}")

        # 计分空间统计
        st.markdown("### 计分空间统计")
        
        # 创建一个DataFrame来展示计分空间统计
        space_stats_df = pd.DataFrame([
            {
                "计分空间": space,
                "工位": stats["工位"],
                "组别": stats["组别"],
                "队伍数量": stats["队伍数量"],
                "平均分": f"{stats['平均分']:.1f}",
                "标准差": f"{stats['标准差']:.1f}",
                "最高分": stats["最高分"],
                "最低分": stats["最低分"]
            }
            for space, stats in st.session_state.space_stats.items()
        ]).sort_values(by=["工位", "组别"])
        
        st.dataframe(space_stats_df, use_container_width=True, hide_index=True)

        # 成绩表格
        st.markdown("### 最终成绩排名")
        display_columns = ["计分空间", "计分空间内排名", "组别", "组内排名", "工位", "工位内排名", "队伍名称", "原始平均分", "最终成绩"]
        
        st.dataframe(
            st.session_state.result_data[display_columns],
            use_container_width=True,
            hide_index=True
        )

        # 导出按钮
        col1, col2 = st.columns(2)
        with col1:
            # Excel导出
            excel_buffer = BytesIO()
            with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
                # 调整导出的字段顺序：按照指定顺序排列
                export_columns = ["组别", "工位", "队伍名称", "原始平均分", "最终成绩", "计分空间内排名", "组内排名"]
                st.session_state.result_data[export_columns].to_excel(
                    writer, index=False, sheet_name="成绩统计"
                )
            excel_data = excel_buffer.getvalue()
            st.download_button(
                label="导出Excel报表",
                data=excel_data,
                file_name="技能大赛成绩统计.xlsx",
                mime="application/vnd.ms-excel",
                use_container_width=True,  # 使按钮填充整个列宽
            )

        with col2:
            # CSV导出
            # 调整导出的字段顺序：按照指定顺序排列
            export_columns = ["组别", "工位", "队伍名称", "原始平均分", "最终成绩", "计分空间内排名", "组内排名"]
            csv_data = st.session_state.result_data[export_columns].to_csv(index=False).encode("utf-8")
            st.download_button(
                label="导出CSV数据",
                data=csv_data,
                file_name="技能大赛成绩.csv",
                mime="text/csv",
                use_container_width=True,  # 使按钮填充整个列宽
            )

        # 可视化
        if show_dist:
            st.markdown("### 成绩分布分析")
            
            # 获取全局变量中的分组信息，以确保整个应用中使用相同的变量
            all_groups = sorted(st.session_state.result_data["组别"].unique())
            all_stations = sorted(st.session_state.result_data["工位"].unique())
            all_spaces = sorted(st.session_state.result_data["计分空间"].unique())
            
            # 绘制分数分布图 - 按组别
            st.markdown("#### 各组原始平均分分布")
            fig, ax = plt.subplots(figsize=(12, 6))
            
            for group in all_groups:
                group_data = st.session_state.result_data[st.session_state.result_data["组别"] == group]
                sns.kdeplot(
                    group_data["原始平均分"], 
                    label=f"{group} (平均: {group_data['原始平均分'].mean():.1f})",
                    fill=True,
                    alpha=0.3
                )
            
            ax.set_xlabel("原始平均分数", fontsize=12)
            ax.set_ylabel("密度", fontsize=12)
            ax.set_title("各组分数分布对比", fontsize=14)
            ax.grid(True, linestyle="--", alpha=0.3)
            ax.legend()
            st.pyplot(fig)
            
            # 绘制分数分布图 - 按工位
            st.markdown("#### 各工位原始平均分分布")
            fig, ax = plt.subplots(figsize=(12, 6))
            
            for station in all_stations:
                station_data = st.session_state.result_data[st.session_state.result_data["工位"] == station]
                sns.kdeplot(
                    station_data["原始平均分"], 
                    label=f"{station} (平均: {station_data['原始平均分'].mean():.1f})",
                    fill=True,
                    alpha=0.3
                )
            
            ax.set_xlabel("原始平均分数", fontsize=12)
            ax.set_ylabel("密度", fontsize=12)
            ax.set_title("各工位分数分布对比", fontsize=14)
            ax.grid(True, linestyle="--", alpha=0.3)
            ax.legend()
            st.pyplot(fig)
            
            # 绘制最终成绩分布图 - 按组别
            st.markdown("#### 各组最终成绩分布")
            fig, ax = plt.subplots(figsize=(12, 6))
            
            for group in all_groups:
                group_data = st.session_state.result_data[st.session_state.result_data["组别"] == group]
                sns.kdeplot(
                    group_data["最终成绩"], 
                    label=f"{group} (平均: {group_data['最终成绩'].mean():.1f})",
                    fill=True,
                    alpha=0.3
                )
            
            ax.set_xlabel("最终成绩", fontsize=12)
            ax.set_ylabel("密度", fontsize=12)
            ax.set_title("各组最终成绩分布对比", fontsize=14)
            ax.axvline(70, color="red", linestyle="--", label="基准分: 70")
            ax.grid(True, linestyle="--", alpha=0.3)
            ax.legend()
            st.pyplot(fig)
            
            # 绘制最终成绩分布图 - 按工位
            st.markdown("#### 各工位最终成绩分布")
            fig, ax = plt.subplots(figsize=(12, 6))
            
            for station in all_stations:
                station_data = st.session_state.result_data[st.session_state.result_data["工位"] == station]
                sns.kdeplot(
                    station_data["最终成绩"], 
                    label=f"{station} (平均: {station_data['最终成绩'].mean():.1f})",
                    fill=True,
                    alpha=0.3
                )
            
            ax.set_xlabel("最终成绩", fontsize=12)
            ax.set_ylabel("密度", fontsize=12)
            ax.set_title("各工位最终成绩分布对比", fontsize=14)
            ax.axvline(70, color="red", linestyle="--", label="基准分: 70")
            ax.grid(True, linestyle="--", alpha=0.3)
            ax.legend()
            st.pyplot(fig)
            
            # 绘制最终成绩分布图 - 按计分空间
            st.markdown("#### 各计分空间最终成绩分布")
            if len(all_spaces) > 10:
                st.toast("计分空间数量过多，为了可视化效果，仅显示队伍数量最多的10个计分空间", icon="⚠️")
                # 计算每个计分空间的队伍数量
                space_team_counts = {}
                for space in all_spaces:
                    space_team_counts[space] = len(st.session_state.result_data[st.session_state.result_data["计分空间"] == space])
                
                # 取队伍数量最多的10个计分空间
                top_spaces = sorted(space_team_counts.items(), key=lambda x: x[1], reverse=True)[:10]
                display_spaces = [space for space, _ in top_spaces]
            else:
                display_spaces = all_spaces
                
            fig, ax = plt.subplots(figsize=(12, 6))
            
            for space in display_spaces:
                space_data = st.session_state.result_data[st.session_state.result_data["计分空间"] == space]
                sns.kdeplot(
                    space_data["最终成绩"], 
                    label=f"{space} (平均: {space_data['最终成绩'].mean():.1f})",
                    fill=True,
                    alpha=0.3
                )
            
            ax.set_xlabel("最终成绩", fontsize=12)
            ax.set_ylabel("密度", fontsize=12)
            ax.set_title("各计分空间最终成绩分布对比", fontsize=14)
            ax.axvline(70, color="red", linestyle="--", label="基准分: 70")
            ax.grid(True, linestyle="--", alpha=0.3)
            ax.legend()
            st.pyplot(fig)
            
            # 散点图展示转换关系 - 按组别
            st.markdown("#### 原始平均分与标准分关系（按组别）")
            # 确保用于绘图的数据是数值类型
            try:
                fig, ax = plt.subplots(figsize=(10, 6))
                
                for group in all_groups:
                    group_data = st.session_state.result_data[st.session_state.result_data["组别"] == group].copy()
                    
                    # 转换为数值类型
                    group_data["原始平均分"] = pd.to_numeric(group_data["原始平均分"], errors="coerce")
                    group_data["最终成绩"] = pd.to_numeric(group_data["最终成绩"], errors="coerce")
                    
                    # 删除任何NaN值
                    group_data = group_data.dropna(subset=["原始平均分", "最终成绩"])
                    
                    if len(group_data) >= 2:  # 确保至少有两个数据点用于绘图
                        ax.scatter(
                            group_data["原始平均分"], 
                            group_data["最终成绩"],
                            s=80, 
                            alpha=0.7,
                            label=group
                        )
                        
                        # 添加队伍名称作为数据点标签
                        for idx, row in group_data.iterrows():
                            ax.annotate(
                                row["队伍名称"],
                                (row["原始平均分"], row["最终成绩"]),
                                xytext=(5, 5),
                                textcoords='offset points',
                                fontsize=8
                            )
                
                ax.set_title("各组原始平均分与标准分转换关系", fontsize=14)
                ax.set_xlabel("原始平均分数", fontsize=12)
                ax.set_ylabel("最终成绩", fontsize=12)
                ax.grid(True, linestyle="--", alpha=0.3)
                ax.legend()
                
                st.pyplot(fig)
                
                # 散点图展示转换关系 - 按工位
                st.markdown("#### 原始平均分与标准分关系（按工位）")
                fig, ax = plt.subplots(figsize=(10, 6))
                
                for station in all_stations:
                    station_data = st.session_state.result_data[st.session_state.result_data["工位"] == station].copy()
                    
                    # 转换为数值类型
                    station_data["原始平均分"] = pd.to_numeric(station_data["原始平均分"], errors="coerce")
                    station_data["最终成绩"] = pd.to_numeric(station_data["最终成绩"], errors="coerce")
                    
                    # 删除任何NaN值
                    station_data = station_data.dropna(subset=["原始平均分", "最终成绩"])
                    
                    if len(station_data) >= 2:  # 确保至少有两个数据点用于绘图
                        ax.scatter(
                            station_data["原始平均分"], 
                            station_data["最终成绩"],
                            s=80, 
                            alpha=0.7,
                            label=station
                        )
                        
                        # 添加队伍名称作为数据点标签
                        for idx, row in station_data.iterrows():
                            ax.annotate(
                                row["队伍名称"],
                                (row["原始平均分"], row["最终成绩"]),
                                xytext=(5, 5),
                                textcoords='offset points',
                                fontsize=8
                            )
                
                ax.set_title("各工位原始平均分与标准分转换关系", fontsize=14)
                ax.set_xlabel("原始平均分数", fontsize=12)
                ax.set_ylabel("最终成绩", fontsize=12)
                ax.grid(True, linestyle="--", alpha=0.3)
                ax.legend()
                
                st.pyplot(fig)
                
                # 散点图展示转换关系 - 按计分空间
                st.markdown("#### 原始平均分与标准分关系（按计分空间）")
                
                # 与前面类似，限制展示的计分空间数量
                if len(all_spaces) > 8:  # 为了图表清晰度，限制更严格
                    st.toast("计分空间数量过多，为了可视化效果，仅显示队伍数量最多的8个计分空间", icon="⚠️")
                    # 计算每个计分空间的队伍数量
                    space_team_counts = {}
                    for space in all_spaces:
                        space_team_counts[space] = len(st.session_state.result_data[st.session_state.result_data["计分空间"] == space])
                    
                    # 取队伍数量最多的8个计分空间
                    top_spaces = sorted(space_team_counts.items(), key=lambda x: x[1], reverse=True)[:8]
                    display_spaces = [space for space, _ in top_spaces]
                else:
                    display_spaces = all_spaces
                
                fig, ax = plt.subplots(figsize=(10, 6))
                
                for space in display_spaces:
                    space_data = st.session_state.result_data[st.session_state.result_data["计分空间"] == space].copy()
                    
                    # 转换为数值类型
                    space_data["原始平均分"] = pd.to_numeric(space_data["原始平均分"], errors="coerce")
                    space_data["最终成绩"] = pd.to_numeric(space_data["最终成绩"], errors="coerce")
                    
                    # 删除任何NaN值
                    space_data = space_data.dropna(subset=["原始平均分", "最终成绩"])
                    
                    if len(space_data) >= 2:  # 确保至少有两个数据点用于绘图
                        ax.scatter(
                            space_data["原始平均分"], 
                            space_data["最终成绩"],
                            s=80, 
                            alpha=0.7,
                            label=space
                        )
                        
                        # 添加队伍名称作为数据点标签
                        for idx, row in space_data.iterrows():
                            ax.annotate(
                                row["队伍名称"],
                                (row["原始平均分"], row["最终成绩"]),
                                xytext=(5, 5),
                                textcoords='offset points',
                                fontsize=8
                            )
                
                ax.set_title("各计分空间原始平均分与标准分转换关系", fontsize=14)
                ax.set_xlabel("原始平均分数", fontsize=12)
                ax.set_ylabel("最终成绩", fontsize=12)
                ax.grid(True, linestyle="--", alpha=0.3)
                ax.legend()
                
                st.pyplot(fig)
                
                # 添加工位分数分布图
                st.markdown("#### 各工位得分情况")
                
                if not st.session_state.team_data.empty:
                    # 工位得分对比
                    station_data = st.session_state.team_data.copy()
                    
                    fig, ax = plt.subplots(figsize=(10, 6))
                    sns.barplot(x="工位", y="原始分", data=station_data, palette="Blues_d", ax=ax)
                    ax.set_title("各工位得分情况", fontsize=14)
                    ax.set_ylim(0, 100)
                    
                    # 在柱状图上标注数值
                    for p in ax.patches:
                        ax.annotate(
                            f"{p.get_height():.1f}",
                            (p.get_x() + p.get_width() / 2., p.get_height()),
                            ha = 'center',
                            va = 'bottom',
                            fontsize=10
                        )
                    
                    st.pyplot(fig)
                    
                    # 显示工位详细信息
                    st.markdown("#### 工位详细信息")
                    station_info = station_data[["工位", "队伍名称", "组别", "原始分"]].sort_values(by="工位")
                    st.dataframe(
                        station_info,
                        use_container_width=True,
                        hide_index=True
                    )
                    
            except Exception as e:
                st.toast(f"绘图时发生错误: {str(e)}", icon="❌")

# ----------------------------------------- 页脚 ---------------------------------------------- #

st.divider()
st.markdown(
    '<div class="footer">© 2025 世界职业院校技能大赛组委会 | 技术支持：深圳信息职业技术大学</div>',
    unsafe_allow_html=True,
)