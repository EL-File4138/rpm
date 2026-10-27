const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(process.argv[2], 'prop-types.js'), 'utf8');
for (const variant of ['global', 'commonjs', 'amd']) {
    const warnings = [];
    const context = vm.createContext({ console: { error: message => warnings.push(message) } });
    let types;
    if (variant === 'commonjs') context.module = { exports: {} };
    if (variant === 'amd') {
        context.define = (dependencies, factory) => { assert.equal(dependencies.length, 0); types = factory(); };
        context.define.amd = true;
    }
    vm.runInContext(source, context);
    types ??= variant === 'commonjs' ? context.module.exports : context.PropTypes;
    const specification = { count: types.number.isRequired, value: types.shape({ label: types.string }),
        children: types.node, element: types.element, component: types.elementType };
    types.checkPropTypes(specification, { count: 1, value: { label: 'ok' }, children: ['text', 1],
        element: { $$typeof: Symbol.for('react.element'), type: 'div', props: {} },
        component: { $$typeof: Symbol.for('react.forward_ref'), render() {} } }, 'prop', 'Example');
    assert.equal(warnings.length, 0);
    types.checkPropTypes(specification, { count: 'wrong', value: { label: 3 } }, 'prop', 'Example');
    assert(warnings.some(message => message.includes('count') && message.includes('number')));
    assert(warnings.some(message => message.includes('value.label') && message.includes('string')));
    const count = warnings.length;
    types.checkPropTypes(specification, { count: 'wrong', value: { label: 3 } }, 'prop', 'Example');
    assert.equal(warnings.length, count, 'Repeated warnings must be deduplicated');
    types.resetWarningCache();
    types.checkPropTypes(specification, { count: 'wrong' }, 'prop', 'Example');
    assert(warnings.length > count);
    assert.throws(() => types.number({ count: 1 }, 'count', 'Example'), /Calling PropTypes validators directly/);
}
console.log('PropTypes: global/CJS/AMD exports, React 18 elements, validation, warnings and error paths passed');
