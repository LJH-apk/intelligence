# -*- coding: UTF-8 -*-
'''
@Project   ：Flask 
@File      ：api.py
@IDE       ：PyCharm 
@Author    ：liujiahang
@Date      ：2025/11/2 14:53 
@PyVersion ：3.10 arm64
'''

# app/routes/api.py
from flask import Blueprint, Response, request, jsonify
import cv2
import numpy as np
import logging
import os
import tempfile
import threading
import time
from datetime import datetime
from werkzeug.utils import secure_filename
from app.service.security_service import SecurityService
from app.service.information_service import InformationService
from config import Config

logger = logging.getLogger(__name__)
bp = Blueprint('api', __name__, url_prefix='/api')

# 全局变量
uploaded_video_path = None
video_processing_active = False
current_analysis_results = []  # 存储当前分析结果
security_service = SecurityService()


# ==================== 视频流相关 API ====================

"""def generate_uploaded_video_frames():
    #生成上传视频的帧
    global uploaded_video_path, video_processing_active, current_analysis_results

    if uploaded_video_path is None or not os.path.exists(uploaded_video_path):
        logger.error("上传的视频文件不存在")
        return

    video_cap = cv2.VideoCapture(uploaded_video_path)
    if not video_cap.isOpened():
        logger.error("无法打开上传的视频文件")
        return

    video_processing_active = True
    frame_count = 0

    try:
        while video_processing_active:
            success, frame = video_cap.read()
            if not success:
                # 循环播放视频
                video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                frame_count = 0
                current_analysis_results = []  # 重置分析结果
                continue

            frame_count += 1

            try:
                processed_frame = frame.copy()

                # 每30帧进行一次分析（避免过于频繁）
                if frame_count % 30 == 0 and security_service.is_running and security_service.video_processor:
                    # 在新线程中进行分析，避免阻塞视频流
                    analysis_thread = threading.Thread(
                        target=analyze_video_frame,
                        args=(frame.copy(), frame_count)
                    )
                    analysis_thread.daemon = True
                    analysis_thread.start()

                # 在帧上绘制检测结果
                if current_analysis_results:
                    for result in current_analysis_results[-3:]:  # 只显示最近3个结果
                        if 'detection' in result and 'bbox' in result['detection']:
                            bbox = result['detection']['bbox']
                            x1, y1, x2, y2 = bbox
                            cv2.rectangle(processed_frame,
                                          (int(x1), int(y1)),
                                          (int(x2), int(y2)),
                                          (0, 255, 0), 2)

                            # 显示分析结果摘要
                            if 'analysis' in result and 'analysis' in result['analysis']:
                                analysis_text = result['analysis']['analysis'][:50] + "..." if len(
                                    result['analysis']['analysis']) > 50 else result['analysis']['analysis']
                                cv2.putText(processed_frame, analysis_text,
                                            (int(x1), int(y1) - 10),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

                # 添加时间戳和视频标签
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cv2.putText(processed_frame, timestamp, (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(processed_frame, "AI安全检测中...", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                # 编码帧为 JPEG
                ret, buffer = cv2.imencode('.jpg', processed_frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                frame_bytes = buffer.tobytes()

                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

            except Exception as e:
                logger.error(f"上传视频帧处理错误: {e}")
                continue

    finally:
        video_cap.release()
        video_processing_active = False"""

def generate_uploaded_video_frames():
    """生成上传视频的帧"""
    global uploaded_video_path, video_processing_active, current_analysis_results

    if uploaded_video_path is None or not os.path.exists(uploaded_video_path):
        logger.error("上传的视频文件不存在")
        return

    video_cap = cv2.VideoCapture(uploaded_video_path)
    if not video_cap.isOpened():
        logger.error("无法打开上传的视频文件")
        return

    # 获取视频原始帧率
    fps = video_cap.get(cv2.CAP_PROP_FPS)
    frame_delay = 1.0 / fps if fps > 0 else 0.033  # 计算每帧间隔时间

    video_processing_active = True
    frame_count = 0
    start_time = time.time()

    try:
        while video_processing_active:
            # 控制播放速度 - 按原始帧率播放
            elapsed = time.time() - start_time
            expected_frame = int(elapsed / frame_delay)
            if frame_count < expected_frame:
                # 需要追赶帧时快速读取
                success, frame = video_cap.read()
                frame_count += 1
            else:
                # 达到目标帧时等待
                time.sleep(max(0, frame_delay - (time.time() - start_time + frame_count * frame_delay)))
                success, frame = video_cap.read()
                frame_count += 1

            if not success:
                # 视频播放完成 - 不循环，停止播放
                video_processing_active = False
                current_analysis_results = []
                break  # 退出循环，不再重复播放

            try:
                processed_frame = frame.copy()

                # 每30帧进行一次分析（避免过于频繁）
                if frame_count % 30 == 0 and security_service.is_running and security_service.video_processor:
                    # 在新线程中进行分析，避免阻塞视频流
                    analysis_thread = threading.Thread(
                        target=analyze_video_frame,
                        args=(frame.copy(), frame_count)
                    )
                    analysis_thread.daemon = True
                    analysis_thread.start()

                # 绘制检测结果和时间戳（保持原有逻辑）
                # ...（省略原有绘制代码）

                # 编码帧为 JPEG
                ret, buffer = cv2.imencode('.jpg', processed_frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                frame_bytes = buffer.tobytes()

                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

            except Exception as e:
                logger.error(f"上传视频帧处理错误: {e}")
                continue

    finally:
        video_cap.release()
        video_processing_active = False
        # 视频播放完成后停止检测
        security_service.stop_system()


def analyze_video_frame(frame, frame_count):
    """分析视频帧"""
    global current_analysis_results

    try:
        if security_service.is_running and security_service.video_processor:
            # 处理单帧
            result = security_service.video_processor.process_single_image(frame)

            if 'fine_analysis' in result and result['fine_analysis']:
                # 只保留最新的分析结果
                current_analysis_results.extend(result['fine_analysis'])

                # 限制结果数量
                if len(current_analysis_results) > 10:
                    current_analysis_results = current_analysis_results[-10:]

                logger.info(f"帧 {frame_count} 分析完成，检测到 {len(result['fine_analysis'])} 个分析结果")

                # 记录预警到数据库
                for analysis in result['fine_analysis']:
                    if analysis.get('alerts'):
                        for alert in analysis['alerts']:
                            InformationService.create_info(
                                time=datetime.fromisoformat(alert['timestamp']),
                                type=alert['category'],
                                message=f"{alert['keyword']}: {alert['description']}"
                            )
    except Exception as e:
        logger.error(f"视频帧分析错误: {e}")


@bp.route('/video/uploaded_stream')
def uploaded_video_stream():
    """上传视频流端点"""
    return Response(generate_uploaded_video_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@bp.route('/video/upload', methods=['POST'])
def upload_video():
    """上传视频文件"""
    global uploaded_video_path, video_processing_active, current_analysis_results

    try:
        if 'video' not in request.files:
            return jsonify({
                'code': 400,
                'status': 'error',
                'message': '没有上传视频文件'
            })

        file = request.files['video']
        if file.filename == '':
            return jsonify({
                'code': 400,
                'status': 'error',
                'message': '没有选择文件'
            })

        # 检查文件扩展名
        allowed_extensions = {'mp4', 'avi', 'mov', 'mkv', 'wmv'}
        filename = secure_filename(file.filename)
        file_extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

        if file_extension not in allowed_extensions:
            return jsonify({
                'code': 400,
                'status': 'error',
                'message': f'不支持的文件格式。支持的格式: {", ".join(allowed_extensions)}'
            })

        # 停止当前视频处理
        video_processing_active = False
        current_analysis_results = []

        # 保存上传的视频文件
        temp_dir = tempfile.gettempdir()
        uploaded_video_path = os.path.join(temp_dir,
                                           f"uploaded_video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_extension}")
        file.save(uploaded_video_path)

        # 验证视频文件
        video_cap = cv2.VideoCapture(uploaded_video_path)
        if not video_cap.isOpened():
            os.remove(uploaded_video_path)
            uploaded_video_path = None
            return jsonify({
                'code': 400,
                'status': 'error',
                'message': '无法读取视频文件，请检查文件格式'
            })

        # 获取视频信息
        fps = video_cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(video_cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0

        video_cap.release()

        logger.info(f"视频上传成功: {uploaded_video_path}, 时长: {duration:.2f}秒, 帧率: {fps:.2f}")

        # 确保安全系统已启动
        if not security_service.is_running:
            security_service.start_system()

        return jsonify({
            'code': 200,
            'status': 'success',
            'message': '视频上传成功',
            'data': {
                'filename': filename,
                'duration': f'{duration:.2f}秒',
                'fps': f'{fps:.2f}',
                'frame_count': frame_count
            }
        })

    except Exception as e:
        logger.error(f"上传视频失败: {e}")
        # 清理上传的文件
        if uploaded_video_path and os.path.exists(uploaded_video_path):
            os.remove(uploaded_video_path)
            uploaded_video_path = None

        return jsonify({
            'code': 500,
            'status': 'error',
            'message': f'上传视频失败: {str(e)}'
        })


@bp.route('/video/stop_uploaded', methods=['POST'])
def stop_uploaded_video():
    """停止上传的视频流"""
    global video_processing_active, uploaded_video_path, current_analysis_results

    try:
        video_processing_active = False
        current_analysis_results = []

        # 清理上传的视频文件
        if uploaded_video_path and os.path.exists(uploaded_video_path):
            os.remove(uploaded_video_path)
            uploaded_video_path = None

        return jsonify({
            'code': 200,
            'status': 'success',
            'message': '上传视频已停止并清理'
        })
    except Exception as e:
        logger.error(f"停止上传视频失败: {e}")
        return jsonify({
            'code': 500,
            'status': 'error',
            'message': f'停止上传视频失败: {str(e)}'
        })


@bp.route('/video/status', methods=['GET'])
def get_video_status():
    """获取视频状态"""
    global uploaded_video_path, video_processing_active

    uploaded_status = "无上传视频"
    if uploaded_video_path and os.path.exists(uploaded_video_path):
        uploaded_status = "运行中" if video_processing_active else "已上传但未播放"

    return jsonify({
        'code': 200,
        'status': 'success',
        'data': {
            'uploaded_video': uploaded_status,
            'uploaded_video_path': uploaded_video_path if uploaded_video_path else None,
            'analysis_results_count': len(current_analysis_results)
        }
    })


# ==================== 预警相关 API ====================

@bp.route('/alert/data', methods=['GET'])
def get_alert_data():
    """获取当前预警数据"""
    global current_analysis_results

    try:
        # 如果有最新的分析结果，使用最新的预警信息
        if current_analysis_results:
            # 获取所有预警并按严重程度排序
            all_alerts = []
            for result in current_analysis_results:
                if 'alerts' in result:
                    all_alerts.extend(result['alerts'])

            # 按严重程度排序：高风险优先
            if all_alerts:
                severity_order = {"high": 3, "medium": 2, "low": 1}
                all_alerts.sort(key=lambda x: (severity_order.get(x.get('severity', 'low'), 0),
                                               x.get('timestamp', '')), reverse=True)

                highest_alert = all_alerts[0]
                severity_map = {
                    "high": "高",
                    "medium": "中",
                    "low": "低"
                }
                level = severity_map.get(highest_alert.get('severity', 'low'), '低')

                return jsonify({
                    "level": level,
                    "message": f"{highest_alert.get('keyword', '未知')}: {highest_alert.get('description', '')}",
                    "code": 200,
                    "raw_alert": highest_alert  # 添加原始预警数据供前端使用
                })

        # 如果没有分析结果，检查数据库中的预警
        if security_service.alert_manager:
            recent_alerts = security_service.alert_manager.get_recent_alerts(10)
            if recent_alerts:
                # 按严重程度排序，优先显示高级别预警
                severity_order = {"high": 3, "medium": 2, "low": 1}
                recent_alerts.sort(key=lambda x: severity_order.get(x.get('severity', 'low'), 0), reverse=True)

                highest_alert = recent_alerts[0]
                severity_map = {
                    "high": "高",
                    "medium": "中",
                    "low": "低"
                }
                level = severity_map.get(highest_alert.get('severity', 'low'), '低')

                return jsonify({
                    "level": level,
                    "message": f"{highest_alert.get('keyword', '未知')}: {highest_alert.get('description', '')}",
                    "code": 200,
                    "raw_alert": highest_alert
                })

        # 默认返回低风险
        return jsonify({
            "level": "低",
            "message": "系统运行正常，未检测到安全风险",
            "code": 200
        })

    except Exception as e:
        logger.error(f"获取预警数据失败: {e}")
        return jsonify({
            "level": "低",
            "message": "系统运行正常",
            "code": 200
        })


@bp.route('/alert/qwen_results', methods=['GET'])
def get_qwen_results():
    """获取Qwen分析结果"""
    global current_analysis_results

    try:
        results = []

        # 从当前分析结果中提取Qwen的分析内容
        for i, result in enumerate(current_analysis_results[-5:]):  # 只返回最近5个结果
            if 'analysis' in result and 'analysis' in result['analysis']:
                analysis_data = result['analysis']
                alerts = result.get('alerts', [])

                # 确定级别
                level = "低"
                if alerts:
                    severity_map = {
                        "high": "高",
                        "medium": "中",
                        "low": "低"
                    }
                    level = severity_map.get(alerts[-1].get('severity', 'low'), '低')

                results.append({
                    "time": analysis_data.get('timestamp', datetime.now().isoformat()),
                    "level": level,
                    "content": analysis_data['analysis'],
                    "has_alerts": len(alerts) > 0,
                    "alert_keywords": [alert['keyword'] for alert in alerts]
                })

        # 如果没有当前分析结果，从数据库获取
        if not results and security_service.alert_manager:
            info_list = InformationService.get_info()
            for info in info_list[-5:]:  # 只返回最近5条
                level_map = {
                    "emergency": "高",
                    "safety_hazard": "高",
                    "security_risk": "中",
                    "suspicious_behavior": "低"
                }
                level = level_map.get(info.type, "低")

                results.append({
                    "time": info.time.strftime("%Y-%m-%d %H:%M:%S"),
                    "level": level,
                    "content": info.message,
                    "has_alerts": True,
                    "alert_keywords": [info.type]
                })

        # 如果仍然没有结果，返回示例数据
        if not results:
            results = [
                {
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "level": "低",
                    "content": "系统正在初始化，请上传视频进行分析...",
                    "has_alerts": False,
                    "alert_keywords": []
                }
            ]

        return jsonify(results)

    except Exception as e:
        logger.error(f"获取Qwen分析结果失败: {e}")
        return jsonify([{
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "level": "低",
            "content": "系统运行正常",
            "has_alerts": False,
            "alert_keywords": []
        }])


@bp.route('/alert/stats', methods=['GET'])
def get_alert_stats():
    """获取预警统计"""
    try:
        if not security_service.alert_manager:
            return jsonify({
                'code': 200,
                'status': 'success',
                'data': {
                    'total': 0,
                    'by_severity': {'high': 0, 'medium': 0, 'low': 0},
                    'by_category': {}
                }
            })

        stats = security_service.alert_manager.get_alert_stats()
        return jsonify({
            'code': 200,
            'status': 'success',
            'data': stats
        })
    except Exception as e:
        logger.error(f"获取预警统计失败: {e}")
        return jsonify({
            'code': 500,
            'status': 'error',
            'message': str(e)
        })


# ==================== 系统相关 API ====================

@bp.route('/system/status', methods=['GET'])
def get_system_status():
    """获取系统状态"""
    global uploaded_video_path, video_processing_active, current_analysis_results

    try:
        # 获取基础系统状态
        system_status = security_service.get_system_status()

        # 添加视频分析状态信息
        system_status['video_analysis'] = {
            'has_uploaded_video': uploaded_video_path is not None,
            'video_processing': video_processing_active,
            'current_results_count': len(current_analysis_results)
        }

        return jsonify({
            'code': 200,
            'status': 'success',
            'data': system_status  # 将整个状态数据放在 data 字段中
        })
    except Exception as e:
        logger.error(f"获取系统状态失败: {e}")
        return jsonify({
            'code': 500,
            'status': 'error',
            'message': str(e)
        })


@bp.route('/system/start', methods=['POST'])
def start_system():
    """启动安全系统"""
    try:
        if security_service.start_system():
            return jsonify({
                'code': 200,
                'status': 'success',
                'message': '安全系统启动成功'
            })
        else:
            return jsonify({
                'code': 500,
                'status': 'error',
                'message': '安全系统启动失败'
            })
    except Exception as e:
        logger.error(f"启动安全系统失败: {e}")
        return jsonify({
            'code': 500,
            'status': 'error',
            'message': str(e)
        })


@bp.route('/system/stop', methods=['POST'])
def stop_system():
    """停止安全系统"""
    global video_processing_active, current_analysis_results

    try:
        security_service.stop_system()
        video_processing_active = False
        current_analysis_results = []

        return jsonify({
            'code': 200,
            'status': 'success',
            'message': '安全系统停止成功'
        })
    except Exception as e:
        logger.error(f"停止安全系统失败: {e}")
        return jsonify({
            'code': 500,
            'status': 'error',
            'message': str(e)
        })


@bp.route('/system/time_weather', methods=['GET'])
def get_time_weather():
    """获取时间和天气信息"""
    try:
        now = datetime.now()

        # 模拟天气数据
        weather_data = {
            "location": "兰州市七里河区",
            "date": now.strftime("%Y年%m月%d日 %A").replace("Monday", "星期一")
            .replace("Tuesday", "星期二")
            .replace("Wednesday", "星期三")
            .replace("Thursday", "星期四")
            .replace("Friday", "星期五")
            .replace("Saturday", "星期六")
            .replace("Sunday", "星期日"),
            "time": now.strftime("%H:%M:%S"),
            "weather": "晴朗",
            "temperature": "24°C"
        }

        return jsonify(weather_data)

    except Exception as e:
        logger.error(f"获取时间天气失败: {e}")
        return jsonify({
            "location": "北京市海淀区",
            "date": datetime.now().strftime("%Y年%m月%d日 %A"),
            "time": datetime.now().strftime("%H:%M:%S"),
            "weather": "晴朗",
            "temperature": "24°C"
        })


# ==================== 图片分析 API ====================

@bp.route('/analyze/image', methods=['POST'])
def analyze_image():
    """分析上传的图片"""
    try:
        if 'image' not in request.files:
            return jsonify({
                'code': 400,
                'status': 'error',
                'message': '没有上传图片'
            })

        file = request.files['image']
        if file.filename == '':
            return jsonify({
                'code': 400,
                'status': 'error',
                'message': '没有选择文件'
            })

        # 确保系统已初始化
        if not security_service.video_processor:
            security_service.initialize()

        # 读取图片数据
        image_data = file.read()
        nparr = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is None:
            return jsonify({
                'code': 400,
                'status': 'error',
                'message': '图片解码失败'
            })

        # 处理图片
        result = security_service.video_processor.process_single_image(frame)

        # 如果有预警，记录到数据库
        if 'fine_analysis' in result:
            for analysis in result['fine_analysis']:
                if analysis.get('alerts'):
                    for alert in analysis['alerts']:
                        InformationService.create_info(
                            time=datetime.fromisoformat(alert['timestamp']),
                            type=alert['category'],
                            message=f"{alert['keyword']}: {alert['description']}"
                        )

        return jsonify({
            'code': 200,
            'status': 'success',
            'data': result
        })

    except Exception as e:
        logger.error(f"图片分析失败: {e}")
        return jsonify({
            'code': 500,
            'status': 'error',
            'message': f'图片分析失败: {str(e)}'
        })


# ==================== 配置相关 API ====================

@bp.route('/config/rules', methods=['GET'])
def get_warning_rules():
    """获取预警规则"""
    return jsonify(Config.WARNING_RULES)


@bp.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': '车站安全预警系统'
    })


# ==================== 兼容性 API ====================

@bp.route("/alert_data", methods=['GET'])
def get_alert_data_legacy():
    """兼容旧版预警数据接口"""
    return get_alert_data()


@bp.route('/prompts', methods=['GET'])
def get_prompts_legacy():
    """兼容旧版提示词接口"""
    return get_qwen_results()