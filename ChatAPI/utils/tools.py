from PIL import Image
import httpx
import io
path_img = './static'  #源图片存储路径 文件夹

def Split_Picture(filename=None):
    id = filename.split('.')[0]  #分割图片名作为id
    img = Image.open(path_img + '/' + filename)
    if img.mode == "RGBA": img = img.convert('RGB')
    size_img = img.size
    print(size_img)
    weight = int(size_img[0] // 2)  #分割后图片的宽度/2
    height = int(size_img[1] // 2)  #分割后图片的高度/2
    for j in range(2):
        for k in range(2):
            box = (weight * k, height * j, weight * (k + 1), height * (j + 1))
            region = img.crop(box) #起始XY结束XY
            region.save('./static/''{}_{}{}.jpg'.format(id, j, k)) #输出路径


def compress_image(image_path, output_path, target_size_kb):
    # 打开图像文件
    image = Image.open(image_path)

    # 重置图像文件位置
    image.seek(0)

    # 转换为 RGB 模式
    image = image.convert('RGB')

    # 设置目标文件大小（以字节为单位）
    target_size_bytes = target_size_kb * 1024

    # 获取图像的当前质量
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='PNG')
    current_size_bytes = len(image_bytes.getvalue())

    # 如果图像已经小于目标大小，则无需压缩
    if current_size_bytes <= target_size_bytes:
        image.save(output_path)
        return

    # 计算压缩质量的比例
    compress_ratio = target_size_bytes / current_size_bytes

    # 根据压缩比例调整图像质量
    image.save(output_path, format='PNG', optimize=True, quality=int(compress_ratio * 100))


def get_task(task_id):
    # 定义API端点和任务ID
    api_endpoint = 'https://api.midjourney.com/api/task/'
    api_key = "OTIxMzAzMjA1OTE5NDkwMDY4.GTYbiu.1jmqqcKi2gy37tVxdpkkt5X1cnXMWxwlFmzM2Y"
    headers = {"Authorization": f"Bearer {api_key}"}
    # task_id = 'YOUR_TASK_ID'  # 替换为你的任务ID
    # 发送GET请求获取生成进度信息
    response = httpx.get(api_endpoint + task_id,timeout=10)

    if response.status_code == 200:
        # 获取响应的JSON数据
        progress_data = response.json()

        # 检查生成状态
        if progress_data['status'] == 'finished':
            # 生成已完成，可以获取生成结果
            result_url = progress_data['result_url']
            print('生成已完成，结果URL:', result_url)
            return result_url
        else:
            # 生成未完成
            progress = progress_data['progress']
            print('生成进度:', progress)
        return progress
    else:
        print('获取生成进度失败:', response.status_code)


# 路径过滤器装饰器
def uuid_filter(regex):
    def decorator(f):
        def wrapper(*args, **kwargs):
            # 获取路径参数
            path_param = args[0]

            # 检查路径参数是否匹配正则表达式
            if regex.match(path_param):
                # 调用被装饰的视图函数
                return f(*args, **kwargs)
            else:
                return False

        return wrapper

    return decorator

if __name__ == '__main__':
    get_task("1130770505394303046")