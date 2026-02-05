const fs = require('fs');
const path = require('path');

const IGNORES = ['node_modules', '.git', 'dist', 'build'];

const PRIORITY_ORDER = {
	src: ['pages', 'components', 'hooks', 'services', 'utils', 'locales'],
	pages: ['Map', 'About', 'HowItWorks', 'PrivacyPolicy', 'ReportIssue', 'TermsOfUse'],
	components: ['features', 'layout', 'modals'],
	utils: ['types', 'constants', 'helpers'],
	services: ['api']
};

function getSortOrder(parentDir, name) {
	const order = PRIORITY_ORDER[parentDir] || [];
	return order.indexOf(name);
}

function sortItems(items, parentDir) {
	return items.sort((a, b) => {
		const aOrder = getSortOrder(parentDir, a.name);
		const bOrder = getSortOrder(parentDir, b.name);
		if (aOrder === -1 && bOrder === -1) return a.name.localeCompare(b.name);
		if (aOrder === -1) return 1;
		if (bOrder === -1) return -1;
		return aOrder - bOrder;
	});
}

function generateTree(dir, prefix = '') {
	let tree = '';
	const items = fs.readdirSync(dir, { withFileTypes: true });
	const parentName = path.basename(dir);
	const filteredItems = items.filter(
		(item) => !IGNORES.some((ignore) => item.name === ignore) && !item.name.startsWith('.')
	);
	const sortedItems = sortItems(filteredItems, parentName);

	sortedItems.forEach((item, index) => {
		const isLast = index === sortedItems.length - 1;
		const connector = isLast ? '└── ' : '├── ';
		const itemName = item.name + (item.isDirectory() ? '/' : '');
		tree += prefix + connector + itemName + '\n';

		if (item.isDirectory()) {
			const newPrefix = prefix + (isLast ? '    ' : '│   ');
			tree += generateTree(path.join(dir, item.name), newPrefix);
		}
	});

	return tree;
}

console.log('# Frontend Tree\n```\n' + generateTree('.') + '\n```');
