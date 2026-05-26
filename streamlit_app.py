import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
from watermark_remover import SmartWatermarkRemover

st.set_page_config(page_title="AI水印去除工具", page_icon="🖼️", layout="wide")

st.title("🖼️ AI智能水印去除工具")
st.markdown("上传图片，自动或手动去除水印")

# 初始化水印去除器
@st.cache_resource
def get_remover():
    return SmartWatermarkRemover()

remover = get_remover()

# 上传图片
uploaded_file = st.file_uploader("选择图片", type=['png', 'jpg', 'jpeg', 'bmp', 'tiff'])

if uploaded_file is not None:
    # 读取图片
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    if image is None:
        st.error("❌ 无法读取图片，请检查文件格式")
    else:
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("原始图片")
            st.image(image, channels="BGR", use_container_width=True)

        # 选择模式
        mode = st.radio("选择去除模式", ["自动检测", "手动选择区域"], horizontal=True)

        if mode == "自动检测":
            if st.button("🚀 开始自动去除水印", type="primary"):
                with st.spinner("正在检测水印区域..."):
                    try:
                        result = remover.process_auto(image)

                        if not result['watermark_found']:
                            st.warning("⚠️ " + result['message'])
                        else:
                            with col2:
                                st.subheader("处理结果")
                                st.image(result['image'], channels="BGR", use_container_width=True)

                            # 下载按钮
                            result_rgb = cv2.cvtColor(result['image'], cv2.COLOR_BGR2RGB)
                            result_pil = Image.fromarray(result_rgb)
                            buf = io.BytesIO()
                            result_pil.save(buf, format='PNG')
                            byte_im = buf.getvalue()

                            st.download_button(
                                label="💾 下载处理后的图片",
                                data=byte_im,
                                file_name="removed_watermark.png",
                                mime="image/png"
                            )
                            st.success("✅ " + result['message'])

                    except Exception as e:
                        st.error(f"❌ 处理失败: {str(e)}")

        else:  # 手动模式
            st.info("💡 使用下方滑块调整水印区域位置和大小")

            col_x, col_y, col_w, col_h = st.columns(4)
            with col_x:
                x = st.slider("X位置 (%)", 0, 100, 10)
            with col_y:
                y = st.slider("Y位置 (%)", 0, 100, 10)
            with col_w:
                w = st.slider("宽度 (%)", 1, 100, 30)
            with col_h:
                h = st.slider("高度 (%)", 1, 100, 10)

            # 显示预览
            preview = image.copy()
            h_img, w_img = image.shape[:2]
            x_px = int(x / 100 * w_img)
            y_px = int(y / 100 * h_img)
            w_px = int(w / 100 * w_img)
            h_px = int(h / 100 * h_img)

            cv2.rectangle(preview, (x_px, y_px), (x_px + w_px, y_px + h_px), (0, 255, 0), 2)
            st.image(preview, channels="BGR", caption="预览选择区域（绿色框）", use_container_width=True)

            if st.button("🚀 去除选定区域水印", type="primary"):
                with st.spinner("正在处理..."):
                    try:
                        regions = [(x_px, y_px, w_px, h_px)]
                        result = remover.process_manual(image, regions)

                        with col2:
                            st.subheader("处理结果")
                            st.image(result['image'], channels="BGR", use_container_width=True)

                        # 下载按钮
                        result_rgb = cv2.cvtColor(result['image'], cv2.COLOR_BGR2RGB)
                        result_pil = Image.fromarray(result_rgb)
                        buf = io.BytesIO()
                        result_pil.save(buf, format='PNG')
                        byte_im = buf.getvalue()

                        st.download_button(
                            label="💾 下载处理后的图片",
                            data=byte_im,
                            file_name="removed_watermark.png",
                            mime="image/png"
                        )
                        st.success("✅ " + result['message'])

                    except Exception as e:
                        st.error(f"❌ 处理失败: {str(e)}")

st.markdown("---")
st.markdown("📝 支持格式：PNG, JPG, JPEG, BMP, TIFF")
