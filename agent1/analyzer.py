import asyncio
import json
import os
import requests
from dotenv import load_dotenv

from crawl4ai import AsyncWebCrawler

# Load environment variables from .env file
load_dotenv()

class DocumentationAnalyzerAgent:
    def __init__(self):
        self.crawler = AsyncWebCrawler()
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.your_site_url = os.getenv("YOUR_SITE_URL")
        self.your_site_name = os.getenv("YOUR_SITE_NAME")
        self.openrouter_api_base = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "deepseek/deepseek-r1:free" # Or your preferred OpenRouter model

        if not self.openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables.")

    async def analyze_article(self, url: str) -> dict:
        print(f"Analyzing: {url}")
        # 1. Fetch content
        async with self.crawler as crawler_instance:
            scraped_result = await crawler_instance.arun(url=url)
            article_content = scraped_result.markdown # Use the markdown content

        if not article_content:
            return {"error": "Could not fetch article content", "url": url}

        # 2. Initialize the report structure
        report = {
            "url": url,
            "readability": {"assessment": "", "suggestions": []},
            "structure": {"assessment": "", "suggestions": []},
            "completeness": {"assessment": "", "suggestions": []},
            "style_guidelines": {"assessment": "", "suggestions": []}
        }

        # 3. Analyze Readability for a Marketer [cite: 7, 8, 9]
        readability_prompt = f"""
        You are an AI assistant specialized in evaluating documentation for non-technical marketers.
        Analyze the following article content for readability from the perspective of a non-technical marketer[cite: 7].
        Explain why it is readable or not and provide specific, actionable suggestions for improvement[cite: 9].
        Focus on clarity and simplicity for a marketing audience, avoiding technical jargon where possible.

        Content:
        ---
        {article_content}
        ---

        CRITICAL INSTRUCTION: Return ONLY the JSON object, and nothing else. Do not include any conversational text, markdown formatting (like ```json), or explanations outside of the JSON.

        Example JSON structure:
        {{
            "assessment": "This section is generally clear but uses some technical terms.",
            "suggestions": [
                "Simplify 'asynchronous callback' to 'event notification'.",
                "Break down sentence X into two shorter sentences for easier digestion."
            ]
        }}
        """
        readability_response = await self._call_llm(readability_prompt)
        report["readability"].update(readability_response)

        # 4. Analyze Structure and Flow [cite: 10, 11]
        structure_prompt = f"""
        Analyze the structure and flow of the following documentation article[cite: 10, 11].
        Consider headings, subheadings, paragraph length, and use of lists[cite: 10].
        Does the information flow logically? Is it easy to navigate and find specific information[cite: 11]?
        Provide a brief assessment and specific, actionable suggestions for improvement.

        Content:
        ---
        {article_content}
        ---

        CRITICAL INSTRUCTION: Return ONLY the JSON object, and nothing else. Do not include any conversational text, markdown formatting (like ```json), or explanations outside of the JSON.

        Example JSON structure:
        {{
            "assessment": "The article uses clear headings but some paragraphs are too long.",
            "suggestions": [
                "Consider breaking down paragraph Y into multiple shorter paragraphs or a bulleted list.",
                "Ensure headings accurately reflect the content of each section."
            ]
        }}
        """
        structure_response = await self._call_llm(structure_prompt)
        report["structure"].update(structure_response)

        # 5. Analyze Completeness of Information & Examples [cite: 12, 13]
        completeness_prompt = f"""
        Evaluate the completeness of information and examples in the following documentation article[cite: 12, 13].
        Does it provide enough detail for a user to understand and implement the feature or concept[cite: 12]?
        Are there sufficient, clear, and relevant examples[cite: 13]? If not, suggest where examples could be added or improved[cite: 13].
        Provide a brief assessment and specific, actionable suggestions for improvement.

        Content:
        ---
        {article_content}
        ---

        CRITICAL INSTRUCTION: Return ONLY the JSON object, and nothing else. Do not include any conversational text, markdown formatting (like ```json), or explanations outside of the JSON.

        Example JSON structure:
        {{
            "assessment": "The article provides general information but lacks specific code examples for common use cases.",
            "suggestions": [
                "Add a simple code example for tracking a 'Product Viewed' event.",
                "Include a screenshot demonstrating the feature's configuration in the MoEngage UI.",
                "Clarify prerequisites for integrating this feature."
            ]
        }}
        """
        completeness_response = await self._call_llm(completeness_prompt)
        report["completeness"].update(completeness_response)

        # 6. Analyze Adherence to Simplified Style Guidelines [cite: 14, 15, 16, 17]
        style_prompt = f"""
        Analyze the following documentation article based on these simplified style guidelines, focusing on clarity, conciseness, and action-oriented language[cite: 14, 15, 16, 17]:
        - Voice and Tone: Should be customer-focused, clear, and concise[cite: 15].
        - Clarity and Conciseness: Avoid overly complex sentences or jargon that could be simplified[cite: 16].
        - Action-oriented language: Should guide the user effectively[cite: 17].

        Identify areas that deviate from these principles and suggest specific changes[cite: 17]. For example, instead of "Improve readability," suggest "Sentence X is too long and complex; consider breaking it into two shorter sentences"[cite: 20].

        Content:
        ---
        {article_content}
        ---

        CRITICAL INSTRUCTION: Return ONLY the JSON object, and nothing else. Do not include any conversational text, markdown formatting (like ```json), or explanations outside of the JSON.

        Example JSON structure:
        {{
            "assessment": "The article's tone is mostly informative but occasionally uses passive voice, and some sentences are unnecessarily long.",
            "suggestions": [
                "Change 'The SDK can be initialized by...' to 'Initialize the SDK by...'.",
                "Break down the sentence starting 'Furthermore, to ensure optimal performance...' into two more concise sentences.",
                "Replace 'utilize' with 'use' for conciseness."
            ]
        }}
        """
        style_response = await self._call_llm(style_prompt)
        report["style_guidelines"].update(style_response)

        return report

    async def _call_llm(self, prompt: str) -> dict:
        """Helper to call the LLM and parse its JSON response using OpenRouter."""
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json",
        }
        if self.your_site_url:
            headers["HTTP-Referer"] = self.your_site_url
        if self.your_site_name:
            headers["X-Title"] = self.your_site_name

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "response_format": {"type": "json_object"}
        }

        try:
            response = await asyncio.to_thread(
                requests.post,
                self.openrouter_api_base,
                headers=headers,
                data=json.dumps(payload)
            )
            response.raise_for_status()
            llm_api_response = response.json()

            # --- START DEBUGGING (remove these prints in final version) ---
            # print(f"Full OpenRouter API Response: {json.dumps(llm_api_response, indent=2)}")
            # --- END DEBUGGING ---

            llm_output_content = llm_api_response.get('choices', [{}])[0].get('message', {}).get('content')

            # --- START DEBUGGING (remove these prints in final version) ---
            # print(f"Raw LLM Content (before json.loads): \n---\n{llm_output_content}\n---")
            # --- END DEBUGGING ---

            if not llm_output_content:
                print("LLM returned empty content.")
                return {"assessment": "LLM returned empty content.", "suggestions": []}

            # Attempt to parse the content as JSON
            # Clean up potential markdown fences or extra text if LLM still includes them
            cleaned_content = llm_output_content.strip()
            if cleaned_content.startswith("```json"):
                cleaned_content = cleaned_content[len("```json"):].strip()
            if cleaned_content.endswith("```"):
                cleaned_content = cleaned_content[:-len("```")].strip()

            parsed_content = json.loads(cleaned_content)
            return parsed_content

        except requests.exceptions.RequestException as e:
            print(f"HTTP request error to OpenRouter: {e}")
            return {"assessment": f"Error during analysis (API request failed): {e}", "suggestions": []}
        except json.JSONDecodeError as e:
            print(f"JSON decoding error from LLM response: {e}. Raw response text: {llm_output_content}")
            return {"assessment": f"Error during analysis (JSON parsing failed): {e}", "suggestions": []}
        except KeyError as e:
            print(f"Unexpected JSON structure from LLM: Missing key {e}. Full LLM response: {llm_api_response}")
            return {"assessment": f"Error during analysis (unexpected LLM response format): Missing key {e}", "suggestions": []}
        except Exception as e:
            print(f"An unexpected error occurred during LLM call: {e}")
            return {"assessment": f"An unexpected error occurred: {e}", "suggestions": []}

async def main():
    agent = DocumentationAnalyzerAgent()

    urls_to_analyze = [
        "https://developers.moengage.com/hc/en-us/articles/9467044080660-Tracking-Events-7-x-x#h_01H96953S1KHBK0JANKVYDHSM1",
        "https://developers.moengage.com/hc/en-us/articles/4562310959380-Notification-Customisation-11-x-x"
    ]

    # List to hold all analysis reports
    all_analysis_reports = []

    for url in urls_to_analyze:
        analysis_report = await agent.analyze_article(url)
        all_analysis_reports.append(analysis_report)
        print(f"Finished analyzing {url}. Report appended to list.")
        print("\n" + "="*50 + "\n")

    # Define the output file name
    output_filename = "sample_output.json"

    try:
        # Write the combined analysis reports to the JSON file
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(all_analysis_reports, f, indent=2, ensure_ascii=False)
        print(f"All analysis reports saved to {output_filename}")
    except IOError as e:
        print(f"Error writing to file {output_filename}: {e}")


if __name__ == "__main__":
    asyncio.run(main())