const fs = require('fs');
const path = require('path');
const glob = require('fast-glob');
const babelParser = require('@babel/parser');
const traverse = require('@babel/traverse').default;
const { parse } = require('@vue/compiler-sfc');

function parseVueFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf-8');
  const { descriptor } = parse(content);

  const result = {
    filePath,
    template: descriptor.template?.content?.trim() || '',
    script: '',
    className: '',
    methods: [],
    properties: [],
    emits: [],
  };

  if (!descriptor.script || descriptor.script.lang !== 'ts') return null;
  result.script = descriptor.script.content;

  // Babel로 AST 파싱
  const ast = babelParser.parse(result.script, {
    sourceType: 'module',
    plugins: ['typescript', 'decorators-legacy', 'classProperties'],
  });

  traverse(ast, {
    ClassDeclaration(path) {
      const decorators = path.node.decorators || [];
      const isVueComponent = decorators.some(d => {
        return d.expression?.callee?.name === 'Component';
      });

      if (!isVueComponent) return;

      result.className = path.node.id.name;

      path.traverse({
        ClassMethod(methodPath) {
          const methodNode = methodPath.node;
          if (methodNode.kind === 'method') {
            result.methods.push(methodNode.key.name);
          }
        },
        ClassProperty(propPath) {
          const propNode = propPath.node;
          const name = propNode.key.name;
          result.properties.push(name);

          const decorators = propNode.decorators || [];
          decorators.forEach(d => {
            const deco = d.expression;
            if (deco.callee?.name === 'Emit') {
              result.emits.push(name);
            }
          });
        },
      });
    }
  });

  return result;
}

async function extractAllChunks(rootDir, outputFile = 'vue_chunks_ast.json') {
  const files = await glob([`${rootDir}/**/*.vue`], {
    ignore: ['**/node_modules/**', '**/dist/**'],
  });

  const allChunks = [];

  for (const file of files) {
    try {
      const parsed = parseVueFile(file);
      if (parsed) {
        allChunks.push(parsed);
      }
    } catch (err) {
      console.warn(`⚠️ ${file} 파싱 실패:`, err.message);
    }
  }

  fs.writeFileSync(outputFile, JSON.stringify(allChunks, null, 2), 'utf-8');
  console.log(`✅ 총 ${allChunks.length}개 컴포넌트 정보 저장 → ${outputFile}`);
}

extractAllChunks('../repo/vue-ts-realworld-app/src', '../data/vue_chunks_ast.json');
