// TEST-009：前台 JSP 对应目标模板与本地资源的首次红灯。
// 浏览器截图、离线控制台和人工签字在 BATCH-004 补充验收。
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

test('首页、登录、注册保留中文页面与本地资源', () => {
  for (const page of ['index', 'login', 'register']) {
    const html = readFileSync(new URL('../../bookshop_app/templates/' + page + '.html', import.meta.url), 'utf8');
    assert.match(html, /<html[^>]*lang="zh-CN"/);
    assert.match(html, /bootstrap/);
    assert.doesNotMatch(html, /https?:\/\//);
  }
});
