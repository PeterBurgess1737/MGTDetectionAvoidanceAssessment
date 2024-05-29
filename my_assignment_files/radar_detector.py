import torch
import torch.nn.functional as F
import transformers

from ai_detector_helpers import ai_detector_server

DEVICE = "cpu"

DETECTOR = transformers.AutoModelForSequenceClassification.from_pretrained("TrustSafeAI/RADAR-Vicuna-7B")
TOKENIZER = transformers.AutoTokenizer.from_pretrained("TrustSafeAI/RADAR-Vicuna-7B")


def calculate_percentage_change_ai(text):
    with torch.no_grad():
        inputs = TOKENIZER(text, padding=True, truncation=True, max_length=512, return_tensors="pt")
        inputs = {k: v.to(DEVICE) for k, v in inputs.items()}

        output_probs = F.log_softmax(DETECTOR(**inputs).logits, -1)[:, 0].exp().tolist()[0]

        return output_probs


ai_detector_server(calculate_percentage_change_ai)
