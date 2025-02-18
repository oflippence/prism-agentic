<script lang="ts">
	import Flatpickr from 'svelte-flatpickr';
	import 'flatpickr/dist/flatpickr.css';
	import { onMount } from 'svelte';
	
	let value = new Date();
	let flatpickrInstance: any;

	const options = {
		enableTime: false,
		dateFormat: 'Y-m-d',
		altInput: true,
		altFormat: 'F j, Y',
		animate: true,
		position: 'auto',
		allowInput: true,
		parseDate: (datestr: string) => {
			const date = new Date(datestr);
			if (!isNaN(date.getTime())) return date;
			
			const parts = datestr.split(/[/-]/);
			if (parts.length === 3) {
				const day = parseInt(parts[0]);
				const month = parseInt(parts[1]) - 1;
				const year = parseInt(parts[2]);
				const parsed = new Date(year, month, day);
				if (!isNaN(parsed.getTime())) return parsed;
			}
			
			return undefined;
		}
	};

	onMount(() => {
		const style = document.createElement('style');
		style.innerHTML = `
			.flatpickr-calendar {
				background: rgb(var(--color-surface-500));
				color: rgb(var(--color-surface-900));
				font-size: 1.1rem;
				width: 340px !important;
			}
			.flatpickr-day.selected {
				background: rgb(var(--color-primary-500)) !important;
				border-color: rgb(var(--color-primary-500)) !important;
			}
			.flatpickr-day:hover {
				background: rgb(var(--color-primary-300)) !important;
				border-color: rgb(var(--color-primary-300)) !important;
			}
			.flatpickr-day.today {
				border-color: rgb(var(--color-primary-500)) !important;
			}
			.flatpickr-months .flatpickr-month {
				background: rgb(var(--color-primary-500));
				color: white;
			}
			.flatpickr-current-month {
				color: white;
			}
			.flatpickr-monthDropdown-months {
				background: rgb(var(--color-primary-500));
				color: white;
			}
			.flatpickr-weekdays {
				background: rgb(var(--color-primary-500));
			}
			.flatpickr-weekday {
				background: rgb(var(--color-primary-500));
				color: white !important;
			}
			.flatpickr-months .flatpickr-prev-month,
			.flatpickr-months .flatpickr-next-month {
				fill: white !important;
			}
			/* Dark mode styles */
			.dark .flatpickr-calendar {
				background: rgb(var(--color-surface-700));
				color: rgb(var(--color-surface-50));
				box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.3);
			}
			.dark .flatpickr-day {
				color: rgb(var(--color-surface-50));
			}
			.dark .flatpickr-day.flatpickr-disabled {
				color: rgb(var(--color-surface-500));
			}
			.dark .flatpickr-day:hover {
				background: rgb(var(--color-primary-700)) !important;
			}
			.dark .flatpickr-day.selected {
				color: white;
			}
		`;
		document.head.appendChild(style);
	});
</script>

<div class="card p-4">
	<div class="input-group input-group-divider grid-cols-[auto_1fr_auto]">
		<div class="input-group-shim">📅</div>
		<Flatpickr
			bind:value
			{options}
			class="input"
			bind:flatpickr={flatpickrInstance}
			placeholder="Type or select a date..."
		/>
	</div>
</div>

<style>
	:global(.flatpickr-input) {
		background: transparent !important;
	}
</style> 