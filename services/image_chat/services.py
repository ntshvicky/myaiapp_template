import os
from pathlib import Path
from services.gemini import GeminiClient

class ImageChatService:
    def __init__(self):
        self.ai = None

    def send_message(self, session, prompt: str) -> str:
        contents = []
        
        try:
            self.ai = GeminiClient()
            image_path = session.image.image.path
            
            if not os.path.exists(image_path):
                return "Error: Uploaded image file not found on server."
                
            mime_type = {
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".png": "image/png",
                ".webp": "image/webp",
            }.get(Path(image_path).suffix.lower(), "image/png")
            with open(image_path, "rb") as handle:
                image_bytes = handle.read()
            
            # Initialize context with the image
            contents.append(
                self.ai.types.Content(
                    role="user", 
                    parts=[
                        self.ai.types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                        self.ai.types.Part.from_text(text="Here is an image. I will ask you questions about it.")
                    ]
                )
            )
            contents.append(
                self.ai.types.Content(
                    role="model", 
                    parts=[self.ai.types.Part.from_text(text="I have analyzed the image. What would you like to know?")]
                )
            )
            
            # Add existing history
            for m in session.messages.order_by("timestamp"):
                role = "user" if m.sender == "user" else "model"
                contents.append(
                    self.ai.text_content(role, m.content)
                )
            
            # Add current prompt
            contents.append(
                self.ai.text_content("user", prompt)
            )

            return self.ai.generate_text(contents)
        except Exception as e:
            return f"Error analyzing image: {str(e)}"
