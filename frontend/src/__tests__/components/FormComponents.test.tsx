/**
 * MyCRM Frontend - Form Component Tests
 * 
 * Comprehensive tests for form-related components and form handling
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';

// =============================================================================
// Form Component Tests
// =============================================================================

describe('Form Component', () => {
    interface FormProps {
        onSubmit: (data: Record<string, unknown>) => void;
        children: React.ReactNode;
    }

    const MockForm = ({ onSubmit, children }: FormProps) => {
        const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
            e.preventDefault();
            const formData = new FormData(e.currentTarget);
            const data: Record<string, unknown> = {};
            formData.forEach((value, key) => {
                data[key] = value;
            });
            onSubmit(data);
        };

        return (
            <form onSubmit={handleSubmit} data-testid="form">
                {children}
            </form>
        );
    };

    it('renders form with children', () => {
        render(
            <MockForm onSubmit={jest.fn()}>
                <input name="email" placeholder="Email" />
                <button type="submit">Submit</button>
            </MockForm>
        );
        expect(screen.getByTestId('form')).toBeInTheDocument();
        expect(screen.getByPlaceholderText('Email')).toBeInTheDocument();
    });

    it('calls onSubmit with form data', async () => {
        const handleSubmit = jest.fn();
        render(
            <MockForm onSubmit={handleSubmit}>
                <input name="email" placeholder="Email" />
                <button type="submit">Submit</button>
            </MockForm>
        );

        await userEvent.type(screen.getByPlaceholderText('Email'), 'test@example.com');
        await userEvent.click(screen.getByRole('button', { name: 'Submit' }));

        expect(handleSubmit).toHaveBeenCalledWith(expect.objectContaining({
            email: 'test@example.com'
        }));
    });

    it('prevents default form submission', async () => {
        const handleSubmit = jest.fn();
        render(
            <MockForm onSubmit={handleSubmit}>
                <button type="submit">Submit</button>
            </MockForm>
        );

        await userEvent.click(screen.getByRole('button', { name: 'Submit' }));

        expect(handleSubmit).toHaveBeenCalled();
    });
});

// =============================================================================
// Textarea Component Tests
// =============================================================================

describe('Textarea Component', () => {
    const MockTextarea = ({
        value,
        onChange,
        placeholder,
        rows = 3,
        maxLength,
        disabled,
        error
    }: {
        value?: string;
        onChange?: (value: string) => void;
        placeholder?: string;
        rows?: number;
        maxLength?: number;
        disabled?: boolean;
        error?: string;
    }) => (
        <div>
            <textarea
                value={value}
                onChange={(e) => onChange?.(e.target.value)}
                placeholder={placeholder}
                rows={rows}
                maxLength={maxLength}
                disabled={disabled}
                aria-invalid={!!error}
            />
            {error && <span role="alert">{error}</span>}
            {maxLength && value && (
                <span data-testid="char-count">{value.length}/{maxLength}</span>
            )}
        </div>
    );

    it('renders textarea', () => {
        render(<MockTextarea placeholder="Enter description" />);
        expect(screen.getByPlaceholderText('Enter description')).toBeInTheDocument();
    });

    it('handles value changes', async () => {
        const handleChange = jest.fn();
        render(<MockTextarea onChange={handleChange} placeholder="Type here" />);

        await userEvent.type(screen.getByPlaceholderText('Type here'), 'Hello World');

        expect(handleChange).toHaveBeenCalled();
    });

    it('respects maxLength', async () => {
        render(<MockTextarea maxLength={10} value="1234567890" />);
        expect(screen.getByTestId('char-count')).toHaveTextContent('10/10');
    });

    it('can be disabled', () => {
        render(<MockTextarea disabled placeholder="Disabled" />);
        expect(screen.getByPlaceholderText('Disabled')).toBeDisabled();
    });

    it('displays error', () => {
        render(<MockTextarea error="This field is required" />);
        expect(screen.getByRole('alert')).toHaveTextContent('This field is required');
    });
});

// =============================================================================
// Switch/Toggle Component Tests
// =============================================================================

describe('Switch Component', () => {
    const MockSwitch = ({
        checked = false,
        onChange,
        label,
        disabled
    }: {
        checked?: boolean;
        onChange?: (checked: boolean) => void;
        label?: string;
        disabled?: boolean;
    }) => (
        <label>
            <input
                type="checkbox"
                role="switch"
                checked={checked}
                onChange={(e) => onChange?.(e.target.checked)}
                disabled={disabled}
            />
            {label && <span>{label}</span>}
        </label>
    );

    it('renders switch', () => {
        render(<MockSwitch label="Enable notifications" />);
        expect(screen.getByRole('switch')).toBeInTheDocument();
    });

    it('toggles on click', async () => {
        const handleChange = jest.fn();
        render(<MockSwitch onChange={handleChange} label="Toggle" />);

        await userEvent.click(screen.getByRole('switch'));

        expect(handleChange).toHaveBeenCalledWith(true);
    });

    it('reflects checked state', () => {
        render(<MockSwitch checked label="On" />);
        expect(screen.getByRole('switch')).toBeChecked();
    });

    it('can be disabled', () => {
        render(<MockSwitch disabled label="Disabled" />);
        expect(screen.getByRole('switch')).toBeDisabled();
    });
});

// =============================================================================
// Radio Group Component Tests
// =============================================================================

describe('Radio Group Component', () => {
    const MockRadioGroup = ({
        name,
        options,
        value,
        onChange,
        disabled
    }: {
        name: string;
        options: { value: string; label: string }[];
        value?: string;
        onChange?: (value: string) => void;
        disabled?: boolean;
    }) => (
        <div role="radiogroup">
            {options.map((option) => (
                <label key={option.value}>
                    <input
                        type="radio"
                        name={name}
                        value={option.value}
                        checked={value === option.value}
                        onChange={(e) => onChange?.(e.target.value)}
                        disabled={disabled}
                    />
                    {option.label}
                </label>
            ))}
        </div>
    );

    const options = [
        { value: 'option1', label: 'Option 1' },
        { value: 'option2', label: 'Option 2' },
        { value: 'option3', label: 'Option 3' }
    ];

    it('renders all radio options', () => {
        render(<MockRadioGroup name="test" options={options} />);
        expect(screen.getAllByRole('radio')).toHaveLength(3);
    });

    it('selects correct option', () => {
        render(<MockRadioGroup name="test" options={options} value="option2" />);
        expect(screen.getByLabelText('Option 2')).toBeChecked();
    });

    it('calls onChange when option selected', async () => {
        const handleChange = jest.fn();
        render(<MockRadioGroup name="test" options={options} onChange={handleChange} />);

        await userEvent.click(screen.getByLabelText('Option 1'));

        expect(handleChange).toHaveBeenCalledWith('option1');
    });

    it('can be disabled', () => {
        render(<MockRadioGroup name="test" options={options} disabled />);
        screen.getAllByRole('radio').forEach((radio) => {
            expect(radio).toBeDisabled();
        });
    });
});

// =============================================================================
// Slider Component Tests
// =============================================================================

describe('Slider Component', () => {
    const MockSlider = ({
        value,
        onChange,
        min = 0,
        max = 100,
        step = 1,
        disabled,
        label
    }: {
        value: number;
        onChange: (value: number) => void;
        min?: number;
        max?: number;
        step?: number;
        disabled?: boolean;
        label?: string;
    }) => (
        <div>
            {label && <label>{label}</label>}
            <input
                type="range"
                value={value}
                onChange={(e) => onChange(Number(e.target.value))}
                min={min}
                max={max}
                step={step}
                disabled={disabled}
                aria-label={label}
            />
            <span data-testid="slider-value">{value}</span>
        </div>
    );

    it('renders slider', () => {
        render(<MockSlider value={50} onChange={jest.fn()} label="Volume" />);
        expect(screen.getByRole('slider')).toBeInTheDocument();
    });

    it('displays current value', () => {
        render(<MockSlider value={75} onChange={jest.fn()} />);
        expect(screen.getByTestId('slider-value')).toHaveTextContent('75');
    });

    it('handles value change', async () => {
        const handleChange = jest.fn();
        render(<MockSlider value={50} onChange={handleChange} />);

        fireEvent.change(screen.getByRole('slider'), { target: { value: '75' } });

        expect(handleChange).toHaveBeenCalledWith(75);
    });

    it('can be disabled', () => {
        render(<MockSlider value={50} onChange={jest.fn()} disabled />);
        expect(screen.getByRole('slider')).toBeDisabled();
    });

    it('respects min and max', () => {
        render(<MockSlider value={50} onChange={jest.fn()} min={10} max={90} />);
        const slider = screen.getByRole('slider');
        expect(slider).toHaveAttribute('min', '10');
        expect(slider).toHaveAttribute('max', '90');
    });
});

// =============================================================================
// Date Picker Component Tests
// =============================================================================

describe('Date Picker Component', () => {
    const MockDatePicker = ({
        value,
        onChange,
        placeholder = 'Select date',
        disabled,
        minDate,
        maxDate
    }: {
        value?: string;
        onChange?: (date: string) => void;
        placeholder?: string;
        disabled?: boolean;
        minDate?: string;
        maxDate?: string;
    }) => (
        <input
            type="date"
            value={value}
            onChange={(e) => onChange?.(e.target.value)}
            placeholder={placeholder}
            disabled={disabled}
            min={minDate}
            max={maxDate}
            aria-label={placeholder}
        />
    );

    it('renders date picker', () => {
        render(<MockDatePicker placeholder="Select date" />);
        expect(screen.getByLabelText('Select date')).toBeInTheDocument();
    });

    it('displays selected date', () => {
        render(<MockDatePicker value="2025-01-24" />);
        expect(screen.getByDisplayValue('2025-01-24')).toBeInTheDocument();
    });

    it('handles date change', async () => {
        const handleChange = jest.fn();
        render(<MockDatePicker onChange={handleChange} />);

        fireEvent.change(screen.getByLabelText('Select date'), { target: { value: '2025-06-15' } });

        expect(handleChange).toHaveBeenCalledWith('2025-06-15');
    });

    it('can be disabled', () => {
        render(<MockDatePicker disabled placeholder="Disabled" />);
        expect(screen.getByLabelText('Disabled')).toBeDisabled();
    });

    it('respects min and max dates', () => {
        render(
            <MockDatePicker
                minDate="2025-01-01"
                maxDate="2025-12-31"
                placeholder="Date picker"
            />
        );
        const input = screen.getByLabelText('Date picker');
        expect(input).toHaveAttribute('min', '2025-01-01');
        expect(input).toHaveAttribute('max', '2025-12-31');
    });
});

// =============================================================================
// File Upload Component Tests
// =============================================================================

describe('File Upload Component', () => {
    const MockFileUpload = ({
        onUpload,
        accept,
        multiple,
        disabled,
        maxSize
    }: {
        onUpload?: (files: FileList | null) => void;
        accept?: string;
        multiple?: boolean;
        disabled?: boolean;
        maxSize?: number;
    }) => (
        <div>
            <input
                type="file"
                onChange={(e) => onUpload?.(e.target.files)}
                accept={accept}
                multiple={multiple}
                disabled={disabled}
                data-testid="file-input"
            />
            {maxSize && <span>Max size: {maxSize}MB</span>}
        </div>
    );

    it('renders file input', () => {
        render(<MockFileUpload />);
        expect(screen.getByTestId('file-input')).toBeInTheDocument();
    });

    it('handles file selection', async () => {
        const handleUpload = jest.fn();
        render(<MockFileUpload onUpload={handleUpload} />);

        const file = new File(['test'], 'test.pdf', { type: 'application/pdf' });
        const input = screen.getByTestId('file-input');

        await userEvent.upload(input, file);

        expect(handleUpload).toHaveBeenCalled();
    });

    it('accepts specific file types', () => {
        render(<MockFileUpload accept=".pdf,.doc,.docx" />);
        expect(screen.getByTestId('file-input')).toHaveAttribute('accept', '.pdf,.doc,.docx');
    });

    it('allows multiple files', () => {
        render(<MockFileUpload multiple />);
        expect(screen.getByTestId('file-input')).toHaveAttribute('multiple');
    });

    it('can be disabled', () => {
        render(<MockFileUpload disabled />);
        expect(screen.getByTestId('file-input')).toBeDisabled();
    });

    it('shows max size info', () => {
        render(<MockFileUpload maxSize={10} />);
        expect(screen.getByText('Max size: 10MB')).toBeInTheDocument();
    });
});

// =============================================================================
// Search Input Component Tests
// =============================================================================

describe('Search Input Component', () => {
    const MockSearchInput = ({
        value,
        onChange,
        onSearch,
        placeholder = 'Search...',
        loading
    }: {
        value?: string;
        onChange?: (value: string) => void;
        onSearch?: (value: string) => void;
        placeholder?: string;
        loading?: boolean;
    }) => (
        <div>
            <input
                type="search"
                value={value}
                onChange={(e) => onChange?.(e.target.value)}
                onKeyDown={(e) => {
                    if (e.key === 'Enter' && value) {
                        onSearch?.(value);
                    }
                }}
                placeholder={placeholder}
            />
            {loading && <span data-testid="loading">Loading...</span>}
        </div>
    );

    it('renders search input', () => {
        render(<MockSearchInput placeholder="Search contacts" />);
        expect(screen.getByPlaceholderText('Search contacts')).toBeInTheDocument();
    });

    it('handles value changes', async () => {
        const handleChange = jest.fn();
        render(<MockSearchInput onChange={handleChange} />);

        await userEvent.type(screen.getByRole('searchbox'), 'test query');

        expect(handleChange).toHaveBeenCalled();
    });

    it('triggers search on Enter', async () => {
        const handleSearch = jest.fn();
        render(<MockSearchInput value="test" onSearch={handleSearch} />);

        await userEvent.type(screen.getByRole('searchbox'), '{enter}');

        expect(handleSearch).toHaveBeenCalledWith('test');
    });

    it('shows loading state', () => {
        render(<MockSearchInput loading />);
        expect(screen.getByTestId('loading')).toBeInTheDocument();
    });
});

// =============================================================================
// OTP Input Component Tests
// =============================================================================

describe('OTP Input Component', () => {
    const MockOTPInput = ({
        length = 6,
        value,
        onChange,
        error
    }: {
        length?: number;
        value?: string;
        onChange?: (value: string) => void;
        error?: string;
    }) => (
        <div>
            <div data-testid="otp-inputs">
                {Array.from({ length }).map((_, i) => (
                    <input
                        // Using index-based key is acceptable here since:
                        // 1. The list is static and never reordered  
                        // 2. Items are not filtered or removed
                        // 3. Each input position represents a specific digit slot
                        // eslint-disable-next-line react/no-array-index-key
                        key={`otp-digit-${i}`}
                        type="text"
                        maxLength={1}
                        value={value?.[i] || ''}
                        onChange={(e) => {
                            const newValue = (value || '').split('');
                            newValue[i] = e.target.value;
                            onChange?.(newValue.join(''));
                        }}
                        aria-label={`Digit ${i + 1}`}
                    />
                ))}
            </div>
            {error && <span role="alert">{error}</span>}
        </div>
    );

    it('renders correct number of inputs', () => {
        render(<MockOTPInput length={6} />);
        expect(screen.getAllByRole('textbox')).toHaveLength(6);
    });

    it('displays value across inputs', () => {
        render(<MockOTPInput value="123456" />);
        expect(screen.getByLabelText('Digit 1')).toHaveValue('1');
        expect(screen.getByLabelText('Digit 2')).toHaveValue('2');
    });

    it('handles input change', async () => {
        const handleChange = jest.fn();
        render(<MockOTPInput value="" onChange={handleChange} />);

        await userEvent.type(screen.getByLabelText('Digit 1'), '1');

        expect(handleChange).toHaveBeenCalled();
    });

    it('shows error message', () => {
        render(<MockOTPInput error="Invalid code" />);
        expect(screen.getByRole('alert')).toHaveTextContent('Invalid code');
    });
});

// =============================================================================
// Tag Input Component Tests
// =============================================================================

describe('Tag Input Component', () => {
    const MockTagInput = ({
        tags = [],
        onAddTag,
        onRemoveTag,
        placeholder = 'Add tag...'
    }: {
        tags?: string[];
        onAddTag?: (tag: string) => void;
        onRemoveTag?: (tag: string) => void;
        placeholder?: string;
    }) => {
        const [inputValue, setInputValue] = React.useState('');

        const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
            if (e.key === 'Enter' && inputValue.trim()) {
                onAddTag?.(inputValue.trim());
                setInputValue('');
            }
        };

        return (
            <div>
                <div data-testid="tags">
                    {tags.map((tag) => (
                        <span key={tag} data-testid={`tag-${tag}`}>
                            {tag}
                            <button onClick={() => onRemoveTag?.(tag)} aria-label={`Remove ${tag}`}>
                                ×
                            </button>
                        </span>
                    ))}
                </div>
                <input
                    type="text"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder={placeholder}
                />
            </div>
        );
    };

    it('renders existing tags', () => {
        render(<MockTagInput tags={['tag1', 'tag2', 'tag3']} />);
        expect(screen.getByTestId('tag-tag1')).toBeInTheDocument();
        expect(screen.getByTestId('tag-tag2')).toBeInTheDocument();
        expect(screen.getByTestId('tag-tag3')).toBeInTheDocument();
    });

    it('adds tag on Enter', async () => {
        const handleAddTag = jest.fn();
        render(<MockTagInput onAddTag={handleAddTag} />);

        await userEvent.type(screen.getByPlaceholderText('Add tag...'), 'newtag{enter}');

        expect(handleAddTag).toHaveBeenCalledWith('newtag');
    });

    it('removes tag on click', async () => {
        const handleRemoveTag = jest.fn();
        render(<MockTagInput tags={['removeme']} onRemoveTag={handleRemoveTag} />);

        await userEvent.click(screen.getByLabelText('Remove removeme'));

        expect(handleRemoveTag).toHaveBeenCalledWith('removeme');
    });
});
