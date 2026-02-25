import { useState, useEffect, useCallback } from 'react';

type Theme = 'light' | 'dark';

export function useTheme() {
	const [theme, setTheme] = useState<Theme>(() => {
		const saved = localStorage.getItem('theme');
		if (saved === 'light' || saved === 'dark') return saved;
		return globalThis.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
	});

	const toggleTheme = useCallback(() => {
		setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
	}, []);

	// Sync DOM + localStorage
	useEffect(() => {
		const root = document.documentElement;
		root.classList.remove('light', 'dark');
		root.classList.add(theme);
		localStorage.setItem('theme', theme);
	}, [theme]);

	// System changes + multi-tab sync
	useEffect(() => {
		const mediaQuery = globalThis.matchMedia('(prefers-color-scheme: dark)');

		const handleSystemChange = (e: MediaQueryListEvent) => {
			if (!localStorage.getItem('theme')) {
				setTheme(e.matches ? 'dark' : 'light');
			}
		};

		const handleStorageChange = (e: StorageEvent) => {
			if (e.key === 'theme' && (e.newValue === 'light' || e.newValue === 'dark')) {
				setTheme(e.newValue as Theme);
			}
		};

		mediaQuery.addEventListener('change', handleSystemChange);
		globalThis.addEventListener('storage', handleStorageChange);

		return () => {
			mediaQuery.removeEventListener('change', handleSystemChange);
			globalThis.removeEventListener('storage', handleStorageChange);
		};
	}, []);

	return { theme, toggleTheme };
}
