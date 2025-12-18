import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from utils import query_tinybird

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# Define schema for the model
SCHEMA_INFO = """
Table: servings_apr_25
Columns:
- day (Date)
- food_name (String)
- amount (String)
- energy_kcal (Float32) - Calories
- carbs_g (Float32)
- fat_g (Float32)
- protein_g (Float32)
- sugars_g (Float32, Nullable)
- water_g (Float32, Nullable)
- group (String)
- alcohol_g (Float32, Nullable)
- caffeine_mg (Float32, Nullable)
- b1_thiamine_mg (Float32, Nullable)
- b2_riboflavin_mg (Float32, Nullable)
- b3_niacin_mg (Float32, Nullable)
- b5_pantothenic_acid_mg (Float32, Nullable)
- b6_pyridoxine_mg (Float32, Nullable)
- b12_cobalamin_g (Float32, Nullable)
- choline_mg (Float32, Nullable)
- folate_g (Float32, Nullable)
- vitamin_a_g (Float32, Nullable)
- vitamin_c_mg (Float32, Nullable)
- vitamin_d_iu (Float32, Nullable)
- vitamin_e_mg (Float32, Nullable)
- vitamin_k_g (Float32, Nullable)
- calcium_mg (Float32, Nullable)
- copper_mg (Float32, Nullable)
- iron_mg (Float32, Nullable)
- magnesium_mg (Float32, Nullable)
- manganese_mg (Float32, Nullable)
- phosphorus_mg (Float32, Nullable)
- potassium_mg (Float32, Nullable)
- selenium_g (Float32, Nullable)
- sodium_mg (Float32, Nullable)
- zinc_mg (Float32, Nullable)
- fiber_g (Float32, Nullable)
- starch_g (Float32, Nullable)
- added_sugars_g (Float32, Nullable)
- net_carbs_g (Float32)
- cholesterol_mg (Float32, Nullable)
- monounsaturated_g (Float32, Nullable)
- polyunsaturated_g (Float32, Nullable)
- saturated_g (Float32, Nullable)
- trans_fats_g (Float32, Nullable)
- omega_3_g (Float32, Nullable)
- omega_6_g (Float32, Nullable)
- cystine_g (Float32, Nullable)
- histidine_g (Float32, Nullable)
- isoleucine_g (Float32, Nullable)
- leucine_g (Float32, Nullable)
- lysine_g (Float32, Nullable)
- methionine_g (Float32, Nullable)
- phenylalanine_g (Float32, Nullable)
- threonine_g (Float32, Nullable)
- tryptophan_g (Float32, Nullable)
- tyrosine_g (Float32, Nullable)
- valine_g (Float32, Nullable)
- category (String)
"""

SYSTEM_PROMPT = f"""Answer the user's question about the data in the 'servings_apr_25' table. This table contains data about diet, where each row represents a portion of a single food that was eaten on a certain day, with micro and macronutrients
Use the 'query_db' tool to find information related to the user's question

Table schema:
{SCHEMA_INFO}
"""

GRAMMAR_DEFINITION = r"""
// ---------- Punctuation & operators ----------
SP: " "
COMMA: ","
GT: ">"
EQ: "="
SEMI: ";"
LPAR: "("
RPAR: ")"

// ---------- Start ----------
start: select_clause SP "FROM" SP "servings_apr_25" [where_clause] [group_clause] [sort_clause] [limit_clause] SEMI

// ---------- Clauses ----------
select_clause: SP "SELECT" SP expression (COMMA SP expression)*
where_clause: SP "WHERE" SP conditions
group_clause: SP "GROUP BY" SP column
sort_clause: SP "ORDER BY" SP expression SP direction
limit_clause: SP "LIMIT" SP NUMBER

// ---------- Expressions ----------
aggregation: AGG_FUNC LPAR column RPAR
column: IDENTIFIER
expression: column | aggregation


// ---------- Filters ----------
conditions: condition (SP logic_op SP condition)*
condition: IDENTIFIER SP COMPARISON_OPS SP VALUE
logic_op: "AND" | "OR"
direction: "ASC" | "DESC"

// ---------- Regex Matches ----------
AGG_FUNC: "SUM" | "AVG" | "COUNT" | "MAX" | "MIN"
COMPARISON_OPS: /(<=|>=|!=|=|<|>)/
IDENTIFIER: /[A-Za-z_][A-Za-z0-9_]*/
STRING: /'[^']*'/
NUMBER: /[0-9]+/
VALUE: STRING | NUMBER
DATE: /'[0-9]{4}-[0-9]{2}-[0-9]{2}'/
"""

TOOLS = [
    {
        "type": "custom",
        "name": "query_db",
        "description": "executes a read-only query against the 'servings_apr_25' table",
        "format": {
            "type": "grammar",
            "syntax": "lark",
            "definition": GRAMMAR_DEFINITION
        }
    }
]

def get_completion_stream(query):
    previous_response_id = None

    input_items = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": query}
    ]

    while True:
        response = client.responses.create(
            model="gpt-5",
            input=input_items,
            reasoning = {
                "effort": "minimal" # 'none' is only supported at gpt-5.1
            },
            previous_response_id=previous_response_id,
            tools=TOOLS,
            parallel_tool_calls=False,
        )

        # element 0 is reasoning, 1 is tool call (if any)
        response_item = response.output[1] if len(response.output) > 1 else None

        if response_item and response_item.type == "custom_tool_call" and response_item.name == "query_db":
            sql_query = response_item.input
            print(f"calling DB with query: {sql_query}")
            
            # Yield the query event so the frontend can display it
            yield {"type": "query", "data": sql_query}
            
            tool_call_result = query_tinybird(sql_query)

            input_items.append(
                {
                    "type": "function_call_output",
                    "call_id": response_item.call_id,
                    "output": json.dumps(tool_call_result)
                }
            )
        elif response_item: # no tool calls
            final_text = response_item.content[0].text
            
            # Yield the final result
            yield {"type": "result", "data": final_text}
            return
        else:
            raise RuntimeError(f"unexpected response, output length is {len(response)}. Output: {response}")

        
        previous_response_id = response.id

