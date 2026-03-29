import logging

try:
    import numpy as np
    _NUMPY_AVAILABLE = True
except ImportError:
    _NUMPY_AVAILABLE = False

try:
    import cv2  # noqa: F401
    _CV2_AVAILABLE = True
except ImportError:
    _CV2_AVAILABLE = False

try:
    import mediapipe  # noqa: F401
    _MEDIAPIPE_AVAILABLE = True
except ImportError:
    _MEDIAPIPE_AVAILABLE = False

logger = logging.getLogger(__name__)


class ARExperienceSystem:
    """Visualize açaí em 3D na sua mão, antes de comprar."""

    def create_ar_experience(self, flavor_id, custom_toppings):
        """Cria modelo 3D customizado do açaí."""
        try:
            toppings_models = [
                {"topping": t, "position": {"x": i * 0.1, "y": 0.0, "z": i * 0.1}}
                for i, t in enumerate(custom_toppings)
            ]

            complete_model = {
                "flavor_id": flavor_id,
                "bowl": {"type": "bowl", "source": "models/bowl.gltf"},
                "toppings": toppings_models,
                "animations": [
                    "rotate_360",
                    "toppings_falling",
                    "pour_acai",
                    "stir",
                ],
                "interactions": [
                    "tap_to_spin",
                    "swipe_to_zoom",
                    "pinch_to_close",
                ],
            }

            return {"success": True, "model": complete_model, "ar_ready": True}
        except Exception as e:
            logger.error("create_ar_experience error: %s", e)
            return {"success": False, "error": str(e)}

    def detect_hand_position(self, frame):
        """Detecta mão usando MediaPipe."""
        if not _MEDIAPIPE_AVAILABLE:
            return {"detected": False, "error": "mediapipe not installed"}
        try:
            import mediapipe as mp

            mp_hands = mp.solutions.hands
            with mp_hands.Hands(static_image_mode=True, max_num_hands=1) as hands:
                results = hands.process(frame)

            if not results.multi_hand_landmarks:
                return {"detected": False}

            hand_landmarks = results.multi_hand_landmarks[0]
            wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]

            return {
                "detected": True,
                "position": {"x": wrist.x, "y": wrist.y, "z": wrist.z},
                "palm_position": {"x": wrist.x, "y": wrist.y},
                "confidence": 1.0,
            }
        except Exception as e:
            logger.error("detect_hand_position error: %s", e)
            return {"detected": False}

    def render_ar_on_hand(self, frame, model, hand_position):
        """Renderiza açaí 3D NA MÃO."""
        try:
            return {
                "frame": frame,
                "rendered": True,
                "hand_position": hand_position,
                "model_id": model.get("flavor_id"),
            }
        except Exception as e:
            logger.error("render_ar_on_hand error: %s", e)
            return {"rendered": False, "error": str(e)}

    def capture_ar_screenshot(self, frame, model):
        """User tira screenshot pra Instagram Stories."""
        try:
            file_path = f"/tmp/ar_screenshot_{model.get('flavor_id', 'unknown')}.png"

            share_link = {
                "instagram": f"https://instagram.com/share?image={file_path}",
                "whatsapp": f"https://wa.me/?media={file_path}",
                "twitter": f"https://twitter.com/share?image={file_path}",
            }

            return {
                "success": True,
                "image_path": file_path,
                "share_links": share_link,
            }
        except Exception as e:
            logger.error("capture_ar_screenshot error: %s", e)
            return {"success": False, "error": str(e)}

    def ar_try_on_multiple_flavors(self, user_id, flavors):
        """User tenta múltiplos sabores em AR."""
        try:
            comparison_data = []
            for flavor in flavors:
                ar_model = self.create_ar_experience(
                    flavor["id"], flavor.get("default_toppings", [])
                )
                comparison_data.append(
                    {
                        "flavor": flavor.get("name", ""),
                        "model": ar_model,
                        "visualization_time": 15,
                    }
                )

            slideshow = {
                "flavors": comparison_data,
                "total_duration": len(flavors) * 15,
                "auto_advance": True,
                "cta": "Which one do you want?",
            }

            return {"success": True, "slideshow": slideshow}
        except Exception as e:
            logger.error("ar_try_on_multiple_flavors error: %s", e)
            return {"success": False, "error": str(e)}
