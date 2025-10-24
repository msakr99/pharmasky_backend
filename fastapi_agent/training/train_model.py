"""
Main script to train the AI agent model
"""
import asyncio
import logging
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from model_trainer import ModelTrainer
from custom_training import CustomTrainer

logger = logging.getLogger(__name__)


async def train_basic_model():
    """Train the basic model with standard data"""
    logger.info("🚀 Starting basic model training...")
    
    trainer = ModelTrainer()
    
    # Load training data
    if not trainer.load_training_data():
        logger.error("❌ Failed to load training data")
        return False
    
    # Train the model
    if await trainer.train_model():
        logger.info("✅ Basic model training completed")
        return True
    else:
        logger.error("❌ Basic model training failed")
        return False


async def train_custom_model():
    """Train the model with custom scenarios"""
    logger.info("🎯 Starting custom model training...")
    
    trainer = CustomTrainer()
    
    # Export training data
    if not trainer.export_training_data():
        logger.error("❌ Failed to export custom training data")
        return False
    
    # Train for each scenario
    success_count = 0
    for scenario in trainer.scenarios.keys():
        if await trainer.train_specialized_model(scenario):
            logger.info(f"✅ Custom training completed for: {scenario}")
            success_count += 1
        else:
            logger.error(f"❌ Custom training failed for: {scenario}")
    
    return success_count == len(trainer.scenarios.keys())


async def evaluate_training():
    """Evaluate the trained model"""
    logger.info("📊 Evaluating trained model...")
    
    trainer = ModelTrainer()
    
    if not trainer.load_training_data():
        logger.error("❌ Failed to load training data for evaluation")
        return False
    
    # Evaluate the model
    score = await trainer.evaluate_model()
    
    if score > 0.7:
        logger.info(f"🎉 Excellent! Model score: {score:.2f}")
        return True
    elif score > 0.5:
        logger.info(f"✅ Good! Model score: {score:.2f}")
        return True
    else:
        logger.warning(f"⚠️ Model needs improvement. Score: {score:.2f}")
        return False


async def main():
    """Main training pipeline"""
    logger.info("🤖 FastAPI AI Agent Model Training")
    logger.info("=" * 50)
    
    # Step 1: Basic training
    logger.info("Step 1: Basic Model Training")
    if await train_basic_model():
        logger.info("✅ Basic training completed")
    else:
        logger.error("❌ Basic training failed")
        return
    
    # Step 2: Custom training
    logger.info("\nStep 2: Custom Scenario Training")
    if await train_custom_model():
        logger.info("✅ Custom training completed")
    else:
        logger.error("❌ Custom training failed")
        return
    
    # Step 3: Evaluation
    logger.info("\nStep 3: Model Evaluation")
    if await evaluate_training():
        logger.info("✅ Model evaluation passed")
    else:
        logger.warning("⚠️ Model evaluation needs improvement")
    
    logger.info("\n🎉 Training pipeline completed!")
    logger.info("The model is now ready for deployment.")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run training
    asyncio.run(main())
