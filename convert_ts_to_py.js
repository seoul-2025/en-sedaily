// Convert TypeScript REPORTER_NAME_MAP to Python dictionary
const fs = require('fs');

// Read the TypeScript file
const tsContent = fs.readFileSync('./frontend/src/constants/reporterNames.ts', 'utf8');

// Extract the REPORTER_NAME_MAP object
const mapMatch = tsContent.match(/export const REPORTER_NAME_MAP: Record<string, string> = \{([\s\S]+?)\};/);
if (!mapMatch) {
  console.error('Could not find REPORTER_NAME_MAP');
  process.exit(1);
}

const mapContent = mapMatch[1];

// Extract all key-value pairs
const entries = mapContent.match(/'[^']+': '[^']+'/g) || [];

console.log(`Found ${entries.length} mappings`);

// Convert to Python format
const pythonEntries = entries.map(entry => {
  // Replace single quotes with double quotes for Python
  return `    ${entry},`;
});

// Create Python file content
const pythonContent = `"""
Byline Translator
Converts Korean reporter names to English using mapping table
Total ${entries.length} mappings from seodaily_byline_data_translated_dedup_byline.xlsx
"""

# Reporter name mapping: Korean → English
REPORTER_NAME_MAP = {
${pythonEntries.join('\n')}
}


def translate_byline(byline: str) -> str:
    """
    Translate Korean reporter name to English

    Args:
        byline: Korean byline (e.g., "김우보 기자", "워싱턴=이태규 특파원")

    Returns:
        English byline (e.g., "Kim U-Bo", "Washington - Lee Tae-Gyu (Correspondent)")
        Falls back to "Seoul Economic Daily" if not found
    """
    if not byline or not byline.strip():
        return "Seoul Economic Daily"

    byline = byline.strip()

    # Try direct lookup in mapping table
    if byline in REPORTER_NAME_MAP:
        return REPORTER_NAME_MAP[byline]

    # If not found, return default
    return "Seoul Economic Daily"


if __name__ == "__main__":
    # Test cases
    test_cases = [
        ("김우보 기자", "Kim U-Bo"),
        ("워싱턴=이태규 특파원", "Washington - Lee Tae-Gyu (Correspondent)"),
        ("Seoul Economic Daily", "Seoul Economic Daily"),
        ("Staff Reporter", "Staff Reporter"),
        ("", "Seoul Economic Daily"),
        ("Unknown Reporter", "Seoul Economic Daily"),
    ]

    print("=== Byline Translation Tests ===\\n")
    for korean, expected in test_cases:
        result = translate_byline(korean)
        status = "✅" if result == expected else "❌"
        print(f"{status} Input: '{korean}'")
        print(f"   Output: {result}")
        print(f"   Expected: {expected}\\n")
`;

// Write to backend utils
fs.writeFileSync('./backend/utils/byline_translator.py', pythonContent);
console.log('✅ Created backend/utils/byline_translator.py with', entries.length, 'mappings');
