import httpx
import streamlit as st

st.set_page_config(page_title="公司知识搜索", page_icon="🔎")
st.title("🔎 公司知识搜索")
st.caption("从 Notion 找到答案，并查看原始出处")

api = st.sidebar.text_input("API 地址", "http://localhost:8000")
if st.sidebar.button("同步 Notion"):
    with st.spinner("正在同步…"):
        try:
            result = httpx.post(f"{api}/sync", timeout=300).json()
            st.sidebar.success(
                f"已同步 {result['pages']} 个页面 / {result['chunks']} 个片段"
            )
        except Exception as exc:
            st.sidebar.error(str(exc))

question = st.chat_input("例如：新员工如何申请开发环境权限？")
if question:
    with st.chat_message("user"):
        st.write(question)
    with st.chat_message("assistant"):
        with st.spinner("正在查找…"):
            try:
                response = httpx.post(f"{api}/ask", json={"question": question}, timeout=120)
                response.raise_for_status()
                data = response.json()
                st.write(data["answer"])
                if data["sources"]:
                    with st.expander("查看来源"):
                        for source in data["sources"]:
                            st.markdown(
                                f"**[{source['title']}]({source['url']})** · "
                                f"相关度 {source['score']:.2f}"
                            )
                            st.caption(source["excerpt"])
            except Exception as exc:
                st.error(f"请求失败：{exc}")
