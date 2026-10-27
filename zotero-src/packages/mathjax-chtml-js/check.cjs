const assert = require('node:assert/strict');
const path = require('node:path');
const root = path.resolve(process.argv[2]);
const load = name => require(path.join(root, 'js', name));
const { mathjax } = load('mathjax.js');
const { TeX } = load('input/tex.js');
const { AllPackages } = load('input/tex/AllPackages.js');
const { CHTML } = load('output/chtml.js');
const { liteAdaptor } = load('adaptors/liteAdaptor.js');
const { RegisterHTMLHandler } = load('handlers/html.js');
assert.equal(mathjax.version, '3.2.2');
const adaptor = liteAdaptor();
RegisterHTMLHandler(adaptor);
const document = mathjax.document('', {
    InputJax: new TeX({ packages: AllPackages }),
    OutputJax: new CHTML({ fontURL: 'mathjax-fonts' }),
});
const render = text => adaptor.outerHTML(document.convert(text, { display: false }));
assert.match(render('\\frac{x}{y}'), /mjx-mfrac/);
assert.match(render('x^2 + \\sqrt{y}'), /mjx-msqrt/);
assert.match(render('\\ce{H2O}'), /mjx-msub/);
assert.match(render('\\frac{a}'), /mjx-merror/);
assert.doesNotMatch(render('z'), /mjx-merror/);
assert.match(adaptor.outerHTML(document.outputJax.styleSheet(document)), /mathjax-fonts/);
console.log('MathJax: original TeX/CHTML modules, chemistry, errors and recovery passed');
