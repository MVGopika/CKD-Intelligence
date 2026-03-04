"""Classification model wrapper"""

def classify_stage(model, features):
    # simplistic stage classification; actual logic lives in model_loader
    return model.predict(features)
