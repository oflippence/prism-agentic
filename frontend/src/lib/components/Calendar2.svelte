<script lang="ts">
	import { onMount } from 'svelte';
	let value = new Date();
	let calendarOpen = false;
	let inputValue = '';
	let inputError = '';
	let isTyping = false;

	// Initialize the input value
	onMount(() => {
		inputValue = formatDate(value);
	});

	function formatDate(date: Date): string {
		return date.toLocaleDateString('en-US', {
			month: 'long',
			day: 'numeric',
			year: 'numeric'
		});
	}

	function parseDate(dateStr: string): Date | null {
		// Try standard formats first
		const date = new Date(dateStr);
		if (!isNaN(date.getTime())) return date;

		// Try DD/MM/YYYY format
		const ddmmyyyy = /^(\d{1,2})[/-](\d{1,2})[/-](\d{4})$/;
		const match = dateStr.match(ddmmyyyy);
		if (match) {
			const [_, day, month, year] = match;
			const parsed = new Date(parseInt(year), parseInt(month) - 1, parseInt(day));
			if (!isNaN(parsed.getTime())) return parsed;
		}

		// Try written format (e.g., "January 1, 2024")
		const written = /^([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})$/;
		const matchWritten = dateStr.match(written);
		if (matchWritten) {
			const [_, month, day, year] = matchWritten;
			const parsed = new Date(`${month} ${day}, ${year}`);
			if (!isNaN(parsed.getTime())) return parsed;
		}

		return null;
	}

	function handleInputChange(event: Event) {
		const input = event.target as HTMLInputElement;
		const newValue = input.value;
		isTyping = true;
		inputValue = newValue;

		// Allow empty input while typing
		if (!newValue.trim()) {
			inputError = '';
			return;
		}

		const parsedDate = parseDate(newValue);
		if (parsedDate) {
			value = parsedDate;
			inputError = '';
		} else {
			inputError = 'Please enter a valid date (e.g., "January 1, 2024" or "DD/MM/YYYY")';
		}
	}

	function handleKeyDown(event: KeyboardEvent) {
		if (event.key === 'Backspace' || event.key === 'Delete') {
			isTyping = true;
			if (event.key === 'Backspace' && inputValue.length === 1) {
				inputValue = '';
				inputError = '';
			}
		} else if (event.key === 'Enter') {
			event.preventDefault();
			const parsedDate = parseDate(inputValue);
			if (parsedDate) {
				value = parsedDate;
				inputValue = formatDate(value);
				inputError = '';
				calendarOpen = false;
				isTyping = false;
				(event.target as HTMLElement).blur();
			}
		} else if (event.key === 'Escape') {
			calendarOpen = false;
			(event.target as HTMLElement).blur();
		}
	}

	function handleInputBlur() {
		isTyping = false;
		// Only reset to the current value if we have an error and we're not actively typing
		if (inputError || (!inputValue.trim() && !isTyping)) {
			inputValue = formatDate(value);
			inputError = '';
		}
		// Don't close the calendar immediately to allow for clicking dates
		setTimeout(() => {
			if (!document.activeElement?.closest('.calendar-popup')) {
				calendarOpen = false;
			}
		}, 200);
	}

	function handleDateSelect(event: MouseEvent) {
		const target = event.target as HTMLElement;
		if (target.matches('.btn-date')) {
			const dateStr = target.getAttribute('data-date');
			if (dateStr) {
				value = new Date(dateStr);
				inputValue = formatDate(value);
				inputError = '';
				calendarOpen = false;
				isTyping = false;
			}
		}
	}

	function generateCalendarDays() {
		const year = value.getFullYear();
		const month = value.getMonth();
		const firstDay = new Date(year, month, 1);
		const lastDay = new Date(year, month + 1, 0);
		const daysInMonth = lastDay.getDate();
		const startingDay = firstDay.getDay();

		const days = [];
		for (let i = 0; i < startingDay; i++) {
			days.push({ date: null, empty: true });
		}

		for (let i = 1; i <= daysInMonth; i++) {
			const date = new Date(year, month, i);
			days.push({
				date,
				today: new Date().toDateString() === date.toDateString(),
				selected: value.toDateString() === date.toDateString()
			});
		}

		return days;
	}

	function prevMonth() {
		value = new Date(value.getFullYear(), value.getMonth() - 1, 1);
	}

	function nextMonth() {
		value = new Date(value.getFullYear(), value.getMonth() + 1, 1);
	}

	// Update input value when calendar value changes, but only if we're not typing
	$: if (value && !isTyping) {
		const formattedDate = formatDate(value);
		if (!inputError && formattedDate !== inputValue) {
			inputValue = formattedDate;
		}
	}
</script>

<div class="card p-4">
	<div class="input-group input-group-divider grid-cols-[auto_1fr_auto] h-[42px]">
		<div class="input-group-shim">📅</div>
		<input
			type="text"
			class="input !min-h-0"
			value={inputValue}
			on:input={handleInputChange}
			on:keydown={handleKeyDown}
			on:blur={handleInputBlur}
			on:focus={() => (calendarOpen = true)}
			placeholder="Type or select a date..."
		/>
	</div>
	{#if inputError}
		<p class="text-error-500 text-sm mt-1">{inputError}</p>
	{/if}

	{#if calendarOpen}
		<div class="calendar-popup" on:mousedown|preventDefault>
			<div class="calendar bg-base-100 rounded-lg shadow-xl p-4">
				<!-- Calendar Header -->
				<div class="flex justify-between items-center mb-4">
					<button class="btn btn-ghost btn-sm" on:click={prevMonth}>
						<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
							<path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
						</svg>
					</button>
					<span class="text-lg font-semibold">
						{value.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
					</span>
					<button class="btn btn-ghost btn-sm" on:click={nextMonth}>
						<svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
							<path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
						</svg>
					</button>
				</div>

				<!-- Calendar Grid -->
				<div class="grid grid-cols-7 gap-1 text-center">
					<!-- Weekday headers -->
					{#each ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'] as day}
						<div class="text-sm font-medium text-primary p-2">{day}</div>
					{/each}

					<!-- Calendar days -->
					{#each generateCalendarDays() as { date, today, selected, empty }}
						{#if empty}
							<div class="p-2"></div>
						{:else}
							<button
								class="btn-date p-2 rounded-lg text-sm hover:bg-primary hover:text-white transition-colors
									{selected ? 'bg-primary text-white' : ''}
									{today ? 'border-2 border-primary' : ''}"
								data-date={date?.toISOString()}
								on:click={handleDateSelect}
							>
								{date?.getDate()}
							</button>
						{/if}
					{/each}
				</div>
			</div>
		</div>
	{/if}
</div>

<style>
	.calendar-popup {
		position: absolute;
		z-index: 50;
		top: calc(100% + 0.5rem);
		left: 0;
		right: 0;
	}

	.calendar {
		position: relative;
		font-size: 1.1rem;
		width: 340px;
	}

	:global(.dark) .calendar {
		background-color: rgb(var(--color-surface-700));
		color: rgb(var(--color-surface-50));
	}

	.btn-date {
		width: 100%;
		height: 100%;
		min-height: 2.5rem;
	}

	.btn-date:hover {
		background-color: rgb(var(--color-primary-500));
		color: white;
	}

	/* Make the card position relative to contain the absolute popup */
	:global(.card) {
		position: relative;
	}
</style> 