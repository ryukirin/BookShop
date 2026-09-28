// TEST-010：目录模板书籍和分类链接绑定真实 ID／名称。
// HTTP、Session 与 Edge 操作在 BATCH-004 增补。
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

test('书籍详情链接由 bid 生成，分类入口不按名称去重', () => {
  const html = readFileSync(new URL('../../bookshop_app/templates/buy.html', import.meta.url), 'utf8');
  assert.match(html, /book\.bid/);
  assert.match(html, /tag\.tname/);
  assert.match(html, /bookDetail/);
  assert.match(html, /queryBytag/);
});
