<img width="1584" height="396" alt="gemini header" src="https://github.com/user-attachments/assets/c9b56136-1059-4c32-991f-e5df6d56c4ce" />

# How to get your Gemini Key?
### 🚀 Step 1: Go to Google AI Studio

Google AI Studio is the official platform to generate and manage your Gemini API keys.

🔗 Visit: https://aistudio.google.com/

### 🚀 Step 2: Sign In With Your Google Account

- Click Sign In
- Use your Gmail ID
- Accept terms if prompted
- (Optional) Select your country and agree to policies

### 🚀 Step 3: Open the API Keys Section

Inside Google AI Studio:

- Look on the left sidebar
- Click “API Keys”
- Direct link (works only after login):

🔗 Visit: https://aistudio.google.com/app/apikey

### 🚀 Step 4: Create a New API Key

- Click “Create API key”
- Name your API key (it can be your app's name)
- Select “New Project” in "Choose an imported project"
- Name your project name (it can be anything)
- Verify your API key name and selected project
- Click on "Create Key" button
- Click on first column under key
- Click Copy or download it securely

# Sample Codes
### For people who writes code in JavaScript (Node.js)
```bash
npm install @google/genai
```
```javascript
// index.js
import { GoogleGenAI } from "@google/genai";
import dotenv from "dotenv";
dotenv.config();

const ai = new GoogleGenAI({
  apiKey: process.env.GEMINI_API_KEY,
});

async function run() {
  const response = await ai.models.generateContent({
    model: "gemini-2.5-flash",
    contents: [
      { role: "user", parts: [{ text: "Explain how LLMs work in simple words." }] }
    ],
  });
  console.log(response.text);
}

run().catch(err => {
  console.error("Error generating content:", err);
});
```

### For people who writes code in Python
```bash
pip install google-genai python-dotenv
```
```python
from dotenv import load_dotenv
from google import genai
client = genai.Client()

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="How does AI work?"
)
print(response.text)
```

### For people who writes code in Java
```xml
<dependency>
  <groupId>com.google.genai</groupId>
  <artifactId>google-genai</artifactId>
  <version>1.0.0</version>
</dependency>
```
```java
import com.google.genai.Client;
import com.google.genai.types.GenerateContentResponse;

public class GenerateContentWithTextInput {
  public static void main(String[] args) {

    Client client = new Client();

    GenerateContentResponse response =
        client.models.generateContent("gemini-2.5-flash", "How does AI work?", null);

    System.out.println(response.text());
  }
}
```
### 🔗 Visit: [Detailed Hackathon Guide](https://gist.github.com/dynamicwebpaige/dcecdf3a3c4bcd9b3dac992bdb647593)

# Project Examples
1. [Leetburns](https://leetburns.vercel.app/) (Already Developed)
2. Resume RAG Bot
3. Notes RAG Chat Bot
