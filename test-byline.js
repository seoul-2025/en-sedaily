// Quick test of byline conversion logic
const REPORTER_NAME_MAP = {
  '강도림 기자': 'Kang Do-Rim',
  '김우보 기자': 'Kim U-Bo',
  '워싱턴=이태규 특파원': 'Washington - Lee Tae-Gyu (Correspondent)',
  'Seoul Economic Daily': 'Seoul Economic Daily',
  'Staff Reporter': 'Staff Reporter',
};

function convertByline(byline) {
  if (!byline || byline.trim() === '') {
    return 'By Seoul Economic Daily';
  }

  try {
    const original = byline.trim();

    // 1. Check full byline first (with titles)
    if (REPORTER_NAME_MAP[original]) {
      return `By ${REPORTER_NAME_MAP[original]}`;
    }

    // 2. If not found, return default
    return 'By Seoul Economic Daily';
  } catch (error) {
    return 'By Seoul Economic Daily';
  }
}

// Test cases
console.log('=== Byline Conversion Tests ===\n');

console.log('Test 1 - Full Korean byline with 기자:');
console.log('Input:', '강도림 기자');
console.log('Output:', convertByline('강도림 기자'));
console.log('Expected: By Kang Do-Rim');
console.log('✅ Match:', convertByline('강도림 기자') === 'By Kang Do-Rim');
console.log('');

console.log('Test 2 - Korean correspondent:');
console.log('Input:', '워싱턴=이태규 특파원');
console.log('Output:', convertByline('워싱턴=이태규 특파원'));
console.log('Expected: By Washington - Lee Tae-Gyu (Correspondent)');
console.log('✅ Match:', convertByline('워싱턴=이태규 특파원') === 'By Washington - Lee Tae-Gyu (Correspondent)');
console.log('');

console.log('Test 3 - Empty byline:');
console.log('Input:', '');
console.log('Output:', convertByline(''));
console.log('Expected: By Seoul Economic Daily');
console.log('✅ Match:', convertByline('') === 'By Seoul Economic Daily');
console.log('');

console.log('Test 4 - Staff Reporter:');
console.log('Input:', 'Staff Reporter');
console.log('Output:', convertByline('Staff Reporter'));
console.log('Expected: By Staff Reporter');
console.log('✅ Match:', convertByline('Staff Reporter') === 'By Staff Reporter');
console.log('');

console.log('Test 5 - Unmapped reporter:');
console.log('Input:', '홍길동 기자');
console.log('Output:', convertByline('홍길동 기자'));
console.log('Expected: By Seoul Economic Daily (falls back)');
console.log('✅ Match:', convertByline('홍길동 기자') === 'By Seoul Economic Daily');
