import fitz # PyMuPDF
import os
from services.gemini import GeminiClient, GeminiError

class DocumentChatService:
    def __init__(self):
        self.ai = None

    def _extract_text_from_pdf(self, file_path, pages_str):
        try:
            doc = fitz.open(file_path)
            text = ""
            
            target_pages = set()
            if pages_str and pages_str.strip().lower() != "all":
                # Parse format like "1-3, 5"
                parts = pages_str.split(',')
                for p in parts:
                    p = p.strip()
                    if '-' in p:
                        start, end = p.split('-')
                        if start.isdigit() and end.isdigit():
                            target_pages.update(range(int(start)-1, int(end)))
                    elif p.isdigit():
                        target_pages.add(int(p)-1)
            
            for i, page in enumerate(doc):
                if pages_str.strip().lower() == "all" or i in target_pages:
                    text += f"\n--- Page {i+1} ---\n"
                    text += page.get_text() + "\n"
            doc.close()
            return text
        except Exception as e:
            return f"Error extracting text: {str(e)}"

    def send_message(self, session, user_input):
        contents = []
        
        try:
            self.ai = GeminiClient()
            pdf_path = session.document.file.path
            if not os.path.exists(pdf_path):
                return "Error: Document file not found on server."
                
            pdf_text = self._extract_text_from_pdf(pdf_path, session.pages)
            
            # Initialize context with the document text
            context_prompt = f"Here is the extracted text from the document (Pages selected: {session.pages}):\n\n{pdf_text}\n\nI will ask you questions about this document."
            
            contents.append(
                self.ai.text_content("user", context_prompt)
            )
            contents.append(
                self.ai.text_content("model", "I have analyzed the document. What would you like to know?")
            )
            
            # Add existing history
            for m in session.messages.order_by("timestamp"):
                role = "user" if m.sender == "user" else "model"
                contents.append(
                    self.ai.text_content(role, m.content)
                )
            
            # Add new user prompt
            contents.append(
                self.ai.text_content("user", user_input)
            )

            return self.ai.generate_text(contents)
        except Exception as e:
            return f"Error analyzing document: {str(e)}"
