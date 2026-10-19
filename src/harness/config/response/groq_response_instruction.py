# Използвайте нативно извикване на функция, когато заявката на потребителя изисква наличен инструмент.
# Не описвайте извикването на функция в текст или JSON съдържание. Извикайте функцията.
# При извикване на функция оставете съдържанието на съобщението празно.
#
# Пример:
# Потребител: "Създай файл hello.txt със съдържание Здравей, свят."
#
# {
#   "id": "chatcmpl-example123",
#   "object": "chat.completion",
#   "created": 1792314000,
#   "model": "llama-3.3-70b-versatile",
#   "choices": [
#     {
#       "index": 0,
#       "message": {
#         "role": "assistant",
#         "content": null,
#         "tool_calls": [
#           {
#             "id": "call_123",
#             "type": "function",
#             "function": {
#               "name": "write_file",
#               "arguments": "{\"path\":\"hello.txt\",\"content\":\"Здравей, свят\"}"
#             }
#           }
#         ]
#       },
#       "finish_reason": "tool_calls"
#     }
#   ],
#   "usage": {
#     "prompt_tokens": 150,
#     "completion_tokens": 30,
#     "total_tokens": 180
#   }
# }
# Извикването на функция се връща в message.tool_calls,
# а не като JSON текст в message.content.



# ============================================================
# Обяснение: tool_result_summaries
# ============================================================
#
# Оригинална инструкция:
#
# Масивът tool_result_summaries съдържа обекти с точно
# id и summary, като и двете са низове.
#
# Значение:
#
# Моделът трябва да обобщи резултатите от изпълнени по-рано инструменти.
#
# Всеки обект за обобщение трябва да съдържа точно две полета от тип низ:
#
# - id: Оригиналният ID, зададен на резултата от изпълнения инструмент.
# - summary: Кратко обобщение на изхода от този инструмент.
#
# Моделът никога не трябва да измисля ID на резултати.
# Ако няма резултати за обобщаване, върнете празен масив.
#
# ------------------------------------------------------------
# Пример
# ------------------------------------------------------------
#
# Заявка на потребителя:
# "Прочети config.py и обясни съдържанието му."
#
# Harness изпълнява:
# read_file(path="config.py")
#
# Примерен резултат от инструмент:
#
# ID на резултата от инструмента: result_123
# Изход: Файлът съдържа настройки за конфигурацията на приложението.
#
# Очакван отговор на модела (message.content):
#
# {
#   "text": "Файлът config.py съдържа настройки за конфигурацията на приложението.",
#   "tool_calls": [],
#   "tool_result_summaries": [
#     {
#       "id": "result_123",
#       "summary": "config.py е прочетен успешно. Файлът съдържа настройки за конфигурацията на приложението."
#     }
#   ]
# }
#
# Важно:
#
# - "result_123" трябва да е действителен ID, предоставен от Harness.
# - "summary" описва резултата от изпълнения по-рано инструмент.
# - "tool_calls" е празно, защото не се заявява нов инструмент.
# - Този JSON се връща в message.content, а не в message.tool_calls.
# - Това е илюстративен пример, а не действителен отговор на модела.
#
# Коментарите са само документация за разработчици.
# Те не трябва да се включват в GROQ_RESPONSE_INSTRUCTION.
# ============================================================.



GROQ_RESPONSE_INSTRUCTION = """
Use native function calling when the user's request requires an available tool.
Do not describe a function call in text or JSON content. Invoke the function.
When invoking a function, leave message content empty.

When answering the user without a function call, return only this JSON object:
{
    "text":"Your actual answer",
    "tool_calls":[],
    "tool_result_summaries":[]
}

All three fields are required. The optional tool_result_output_requests field
is an array of original tool result ID strings whose complete outputs you need.
No other fields or Markdown fences are allowed.

The text field is a string. The tool_calls field in content is always empty.
When no native function call is emitted, the text field must not be empty.
If an earlier command instruction requires answer and command_summary, encode
that two-field JSON object inside text exactly as instructed.

The tool_result_summaries array contains objects with exactly id and summary,
both strings. Use only original IDs from actual previously executed results.
If there are no results to summarize, use an empty array. Never invent results.
This JSON object is message content, not a function call. There is no json tool.
Past tool calls and results are supplied as conversation text by the harness.
Messages saying "The requested tools have finished" contain completed results.
Use their Output as the result of the preceding call; do not repeat that call.

"Tool result ID" is an opaque identifier for summaries, never a file path.
After a successful read, answer from the provided Output and summarize that
result using its exact ID. Request another tool only if more work is necessary.
Answer the latest user request; use tools only when that request requires them.
""".strip()
