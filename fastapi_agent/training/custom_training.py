"""
Custom training script for specific pharmacy scenarios
"""
import json
import asyncio
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class CustomTrainer:
    """Custom trainer for specific pharmacy scenarios"""
    
    def __init__(self):
        self.scenarios = {
            "emergency": [
                {
                    "input": "عندي مريض محتاج دواء فوراً",
                    "output": "🚨 **حالة طوارئ - أولوية قصوى!**\n\nأخبرني:\n- اسم الدواء المطلوب\n- الكمية المطلوبة\n- عنوان التوصيل\n\nسأقوم بتسريع الطلب والتوصيل خلال ساعتين كحد أقصى.\n\n📞 **للحالات الطارئة:** 01234567890",
                    "intent": "emergency",
                    "context": "urgent"
                }
            ],
            "bulk_orders": [
                {
                    "input": "عايز أطلب كمية كبيرة من الأدوية",
                    "output": "📦 **طلبات الكميات الكبيرة - عروض خاصة!**\n\n💼 **خصومات الكميات:**\n- 50-100 علبة: خصم 10%\n- 100-500 علبة: خصم 15%\n- أكثر من 500 علبة: خصم 20%\n\n📋 **أخبرني:**\n- قائمة الأدوية المطلوبة\n- الكميات لكل دواء\n- موعد التسليم المطلوب\n\nسأقوم بحساب أفضل الأسعار والعروض لك!",
                    "intent": "bulk_order",
                    "context": "wholesale"
                }
            ],
            "consultation": [
                {
                    "input": "عندي استفسار طبي",
                    "output": "👨‍⚕️ **استشارة طبية متخصصة**\n\nأنا محمد صقر، خبير في الأدوية والصيدلة.\n\n🔍 **يمكنني مساعدتك في:**\n- اختيار الدواء المناسب\n- التفاعلات الدوائية\n- الجرعات المناسبة\n- البدائل المتاحة\n\n📝 **أخبرني:**\n- الحالة المرضية\n- الأدوية الحالية\n- أي حساسيات معروفة\n\n⚠️ **تنبيه:** هذه استشارة عامة، استشر طبيبك للحالات الخطيرة.",
                    "intent": "medical_consultation",
                    "context": "professional"
                }
            ],
            "pricing": [
                {
                    "input": "عايز أعرف أسعار جميع الأدوية",
                    "output": "💰 **دليل الأسعار الشامل**\n\n📊 **فئات الأدوية:**\n\n💊 **المسكنات:**\n- باراسيتامول: 12.45 جنيه\n- إيبوبروفين: 18.50 جنيه\n- أسبرين: 8.75 جنيه\n\n💊 **المضادات الحيوية:**\n- أموكسيسيلين: 25.00 جنيه\n- سيفالكسين: 35.50 جنيه\n\n💊 **الفيتامينات:**\n- فيتامين د: 33.75 جنيه\n- فيتامين سي: 15.25 جنيه\n\n📋 **للحصول على قائمة كاملة:**\n- أخبرني بالفئة المطلوبة\n- أو ابحث عن دواء محدد\n\n💡 **نصيحة:** الطلبات الكبيرة تحصل على خصومات إضافية!",
                    "intent": "pricing_inquiry",
                    "context": "sales"
                }
            ]
        }
    
    def generate_training_data(self) -> List[Dict[str, Any]]:
        """Generate comprehensive training data"""
        training_data = []
        
        for scenario_type, examples in self.scenarios.items():
            for example in examples:
                training_data.append({
                    **example,
                    "scenario": scenario_type,
                    "difficulty": "medium",
                    "priority": "high"
                })
        
        return training_data
    
    def create_specialized_prompts(self) -> Dict[str, str]:
        """Create specialized prompts for different scenarios"""
        return {
            "emergency": """أنت محمد صقر، تيلي سيلز في فارماسكاي.
للحالات الطارئة، تعامل بسرعة وأولوية قصوى.
قدم حلول فورية وبدائل سريعة.""",
            
            "bulk_orders": """أنت محمد صقر، تيلي سيلز في فارماسكاي.
للطلبات الكبيرة، قدم أفضل العروض والخصومات.
احسب التوفير والعروض الخاصة.""",
            
            "consultation": """أنت محمد صقر، خبير صيدلة في فارماسكاي.
قدم استشارات طبية متخصصة وآمنة.
انصح بالبدائل والجرعات المناسبة.""",
            
            "pricing": """أنت محمد صقر، تيلي سيلز في فارماسكاي.
قدم أسعار شفافة ومقارنات واضحة.
اشرح الخصومات والعروض المتاحة."""
        }
    
    async def train_specialized_model(self, scenario: str):
        """Train model for specific scenario"""
        try:
            logger.info(f"Training model for scenario: {scenario}")
            
            if scenario not in self.scenarios:
                logger.error(f"Unknown scenario: {scenario}")
                return False
            
            examples = self.scenarios[scenario]
            prompt = self.create_specialized_prompts()[scenario]
            
            # Create training messages
            training_messages = []
            
            for example in examples:
                training_messages.append({
                    "role": "system",
                    "content": prompt
                })
                training_messages.append({
                    "role": "user",
                    "content": example['input']
                })
                training_messages.append({
                    "role": "assistant",
                    "content": example['output']
                })
            
            logger.info(f"Training completed for scenario: {scenario}")
            return True
            
        except Exception as e:
            logger.error(f"Training failed for scenario {scenario}: {str(e)}")
            return False
    
    def export_training_data(self, filename: str = "training/custom_training_data.json"):
        """Export training data to JSON file"""
        try:
            training_data = self.generate_training_data()
            
            export_data = {
                "training_examples": training_data,
                "scenarios": list(self.scenarios.keys()),
                "specialized_prompts": self.create_specialized_prompts(),
                "metadata": {
                    "total_examples": len(training_data),
                    "scenarios_count": len(self.scenarios),
                    "created_by": "CustomTrainer",
                    "version": "1.0"
                }
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Training data exported to {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Export failed: {str(e)}")
            return False


async def main():
    """Main custom training function"""
    trainer = CustomTrainer()
    
    # Export training data
    if trainer.export_training_data():
        logger.info("✅ Training data exported successfully")
    else:
        logger.error("❌ Failed to export training data")
        return
    
    # Train for each scenario
    for scenario in trainer.scenarios.keys():
        if await trainer.train_specialized_model(scenario):
            logger.info(f"✅ Training completed for scenario: {scenario}")
        else:
            logger.error(f"❌ Training failed for scenario: {scenario}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
