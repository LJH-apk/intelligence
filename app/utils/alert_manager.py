# -*- coding: UTF-8 -*-
'''
@Project   ：Flask 
@File      ：alert_manager.py
@IDE       ：PyCharm 
@Author    ：liujiahang
@Date      ：2025/10/27 15:09 
@PyVersion ：3.10 arm64
'''
from datetime import datetime, timedelta
import logging
import re
from config import Config

logger = logging.getLogger(__name__)


class AlertManager:
    def __init__(self):
        self.alerts = []
        self.warning_rules = Config.WARNING_RULES
        # 添加关键词权重
        self.keyword_weights = self._init_keyword_weights()

    def _init_keyword_weights(self):
        """初始化关键词权重"""
        weights = {
            "suspicious_behavior": {
                "打架": 0.9, "斗殴": 0.9, "追逐": 0.6, "攀爬": 0.7, "翻越": 0.7, "躺卧": 0.3, "聚集": 0.4
            },
            "safety_hazard": {
                "烟火": 0.8, "吸烟": 0.7, "明火": 0.9, "漏电": 0.9, "漏水": 0.6, "摔倒": 0.7, "晕倒": 0.8
            },
            "security_risk": {
                "无人看管的行李": 0.8, "可疑包裹": 0.9, "破坏设备": 0.8, "非法进入": 0.9
            },
            "emergency": {
                "急救": 0.9, "晕厥": 0.8, "突发疾病": 0.8, "事故": 0.9
            }
        }
        return weights

    def add_alert(self, alert_data):
        """添加预警"""
        self.alerts.append(alert_data)

        # 限制数量
        if len(self.alerts) > Config.MAX_ALERTS:
            self.alerts = self.alerts[-Config.MAX_ALERTS:]

        logger.info(
            f"New alert added: {alert_data['category']} - {alert_data['keyword']} - 等级: {alert_data['severity']}")

    def check_analysis_for_alerts(self, analysis_result, detection_info):
        """分析结果生成预警"""
        analysis_text = analysis_result.get('analysis', '').lower()
        alerts_found = []

        # 使用更宽松的匹配方式，包含部分匹配
        for category, keywords in self.warning_rules.items():
            for keyword in keywords:
                keyword_lower = keyword.lower()
                # 使用更宽松的匹配：包含关键词即可
                if keyword_lower in analysis_text:
                    # 计算综合置信度
                    confidence = detection_info.get('confidence', 0)
                    keyword_weight = self.keyword_weights.get(category, {}).get(keyword, 0.5)

                    # 综合评分决定预警等级
                    combined_score = confidence * keyword_weight

                    alert = {
                        'category': category,
                        'keyword': keyword,
                        'description': analysis_result.get('analysis', ''),
                        'bbox': detection_info.get('bbox', []),
                        'confidence': confidence,
                        'timestamp': analysis_result.get('timestamp', datetime.now().isoformat()),
                        'severity': self._calculate_severity_level(category, keyword, combined_score, analysis_text),
                        'type': 'behavior_analysis',
                        'combined_score': combined_score
                    }
                    alerts_found.append(alert)

        # 添加预警
        for alert in alerts_found:
            self.add_alert(alert)

        return alerts_found

    def _calculate_severity_level(self, category, keyword, combined_score, analysis_text):
        """根据综合评分和上下文计算预警等级"""
        # 基础等级映射 - 调整部分类别为高风险
        base_severity_map = {
            "emergency": "high",
            "safety_hazard": "high",  # 安全危害调整为高风险
            "security_risk": "medium",
            "suspicious_behavior": "low"
        }

        base_severity = base_severity_map.get(category, "low")

        # 根据关键词强度调整
        high_risk_keywords = ["打架", "斗殴", "明火", "漏电", "事故", "急救", "晕厥", "突发疾病"]
        if keyword in high_risk_keywords:
            return "high"

        # 根据分析文本中的紧急词汇调整
        emergency_indicators = ["紧急", "危险", "立即", "马上", "救命", "报警", "火灾", "爆炸"]
        if any(indicator in analysis_text for indicator in emergency_indicators):
            return "high"

        # 根据综合评分调整等级
        if combined_score >= 0.5:  # 降低阈值
            return "high"
        elif combined_score >= 0.3:
            return "medium"
        else:
            return "low"

    def get_recent_alerts(self, count=20):
        """获取最近的预警"""
        return self.alerts[-count:] if self.alerts else []

    def get_alerts_by_severity(self, severity):
        """按严重级别获取预警"""
        return [alert for alert in self.alerts if alert.get('severity') == severity]

    def get_high_severity_alerts(self):
        """获取高风险预警"""
        return self.get_alerts_by_severity('high')

    def cleanup_old_alerts(self):
        """清理过期预警"""
        cutoff_time = datetime.now() - timedelta(days=Config.ALERT_RETENTION_DAYS)
        self.alerts = [
            alert for alert in self.alerts
            if datetime.fromisoformat(alert['timestamp']) > cutoff_time
        ]

    def get_alert_stats(self):
        """获取预警统计"""
        stats = {
            'total': len(self.alerts),
            'by_severity': {
                'high': len(self.get_alerts_by_severity('high')),
                'medium': len(self.get_alerts_by_severity('medium')),
                'low': len(self.get_alerts_by_severity('low'))
            },
            'by_category': {}
        }

        for category in self.warning_rules.keys():
            stats['by_category'][category] = len([
                alert for alert in self.alerts
                if alert.get('category') == category
            ])

        return stats