'use client';

import React, { ReactNode, useEffect } from 'react';
import { useForm, FieldValues, UseFormReturn, Path, FieldError, DefaultValues, SubmitHandler } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Switch } from '@/components/ui/switch';
import { Calendar } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Calendar as CalendarIcon, Loader2, AlertCircle } from 'lucide-react';
import { format } from 'date-fns';
import { cn } from '@/lib/utils';

/**
 * Form Builder Components
 * 
 * Provides reusable form components with:
 * - Zod schema validation
 * - Error handling
 * - Loading states
 * - Consistent styling
 */

interface FormFieldProps {
    name: string;
    label?: string;
    description?: string;
    error?: FieldError;
    required?: boolean;
    className?: string;
    children: ReactNode;
}

/**
 * Form field wrapper with label and error handling
 */
export function FormField({
    name,
    label,
    description,
    error,
    required,
    className,
    children,
}: FormFieldProps) {
    return (
        <div className={cn('space-y-2', className)}>
            {label && (
                <Label htmlFor={name} className="flex items-center gap-1">
                    {label}
                    {required && <span className="text-red-500">*</span>}
                </Label>
            )}
            {children}
            {description && !error && (
                <p className="text-sm text-gray-500">{description}</p>
            )}
            {error && (
                <p className="text-sm text-red-600 flex items-center gap-1">
                    <AlertCircle className="h-3 w-3" />
                    {error.message}
                </p>
            )}
        </div>
    );
}

interface TextInputProps<T extends FieldValues> {
    form: UseFormReturn<T>;
    name: Path<T>;
    label?: string;
    description?: string;
    placeholder?: string;
    type?: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url';
    required?: boolean;
    disabled?: boolean;
    className?: string;
}

/**
 * Text input field with form integration
 */
export function TextInput<T extends FieldValues>({
    form,
    name,
    label,
    description,
    placeholder,
    type = 'text',
    required,
    disabled,
    className,
}: TextInputProps<T>) {
    const { register, formState: { errors } } = form;
    const error = errors[name] as FieldError | undefined;

    return (
        <FormField
            name={name}
            label={label}
            description={description}
            error={error}
            required={required}
            className={className}
        >
            <Input
                id={name}
                type={type}
                placeholder={placeholder}
                disabled={disabled}
                {...register(name)}
                className={error ? 'border-red-500' : ''}
            />
        </FormField>
    );
}

interface TextAreaInputProps<T extends FieldValues> {
    form: UseFormReturn<T>;
    name: Path<T>;
    label?: string;
    description?: string;
    placeholder?: string;
    rows?: number;
    required?: boolean;
    disabled?: boolean;
    className?: string;
}

/**
 * Textarea field with form integration
 */
export function TextAreaInput<T extends FieldValues>({
    form,
    name,
    label,
    description,
    placeholder,
    rows = 4,
    required,
    disabled,
    className,
}: TextAreaInputProps<T>) {
    const { register, formState: { errors } } = form;
    const error = errors[name] as FieldError | undefined;

    return (
        <FormField
            name={name}
            label={label}
            description={description}
            error={error}
            required={required}
            className={className}
        >
            <Textarea
                id={name}
                placeholder={placeholder}
                rows={rows}
                disabled={disabled}
                {...register(name)}
                className={error ? 'border-red-500' : ''}
            />
        </FormField>
    );
}

interface SelectInputProps<T extends FieldValues> {
    form: UseFormReturn<T>;
    name: Path<T>;
    label?: string;
    description?: string;
    placeholder?: string;
    options: { value: string; label: string }[];
    required?: boolean;
    disabled?: boolean;
    className?: string;
}

/**
 * Select field with form integration
 */
export function SelectInput<T extends FieldValues>({
    form,
    name,
    label,
    description,
    placeholder = 'Select an option',
    options,
    required,
    disabled,
    className,
}: SelectInputProps<T>) {
    const { watch, setValue, formState: { errors } } = form;
    const error = errors[name] as FieldError | undefined;
    const value = watch(name) as string;

    return (
        <FormField
            name={name}
            label={label}
            description={description}
            error={error}
            required={required}
            className={className}
        >
            <Select
                value={value}
                onValueChange={(v) => setValue(name, v as T[typeof name])}
                disabled={disabled}
            >
                <SelectTrigger className={error ? 'border-red-500' : ''}>
                    <SelectValue placeholder={placeholder} />
                </SelectTrigger>
                <SelectContent>
                    {options.map((option) => (
                        <SelectItem key={option.value} value={option.value}>
                            {option.label}
                        </SelectItem>
                    ))}
                </SelectContent>
            </Select>
        </FormField>
    );
}

interface CheckboxInputProps<T extends FieldValues> {
    form: UseFormReturn<T>;
    name: Path<T>;
    label: string;
    description?: string;
    disabled?: boolean;
    className?: string;
}

/**
 * Checkbox field with form integration
 */
export function CheckboxInput<T extends FieldValues>({
    form,
    name,
    label,
    description,
    disabled,
    className,
}: CheckboxInputProps<T>) {
    const { watch, setValue, formState: { errors } } = form;
    const error = errors[name] as FieldError | undefined;
    const isChecked = watch(name) as boolean;

    return (
        <div className={cn('flex items-start space-x-3', className)}>
            <Checkbox
                id={name}
                checked={isChecked}
                onCheckedChange={(checked) => setValue(name, !!checked as T[typeof name])}
                disabled={disabled}
            />
            <div className="space-y-1 leading-none">
                <Label htmlFor={name} className="cursor-pointer">
                    {label}
                </Label>
                {description && (
                    <p className="text-sm text-gray-500">{description}</p>
                )}
                {error && (
                    <p className="text-sm text-red-600">{error.message}</p>
                )}
            </div>
        </div>
    );
}

interface SwitchInputProps<T extends FieldValues> {
    form: UseFormReturn<T>;
    name: Path<T>;
    label: string;
    description?: string;
    disabled?: boolean;
    className?: string;
}

/**
 * Switch/Toggle field with form integration
 */
export function SwitchInput<T extends FieldValues>({
    form,
    name,
    label,
    description,
    disabled,
    className,
}: SwitchInputProps<T>) {
    const { watch, setValue, formState: { errors } } = form;
    const error = errors[name] as FieldError | undefined;
    const isChecked = watch(name) as boolean;

    return (
        <div className={cn('flex items-center justify-between', className)}>
            <div className="space-y-0.5">
                <Label htmlFor={name}>{label}</Label>
                {description && (
                    <p className="text-sm text-gray-500">{description}</p>
                )}
                {error && (
                    <p className="text-sm text-red-600">{error.message}</p>
                )}
            </div>
            <Switch
                id={name}
                checked={isChecked}
                onCheckedChange={(checked) => setValue(name, checked as T[typeof name])}
                disabled={disabled}
            />
        </div>
    );
}

interface DateInputProps<T extends FieldValues> {
    form: UseFormReturn<T>;
    name: Path<T>;
    label?: string;
    description?: string;
    placeholder?: string;
    required?: boolean;
    disabled?: boolean;
    className?: string;
}

/**
 * Date picker field with form integration
 */
export function DateInput<T extends FieldValues>({
    form,
    name,
    label,
    description,
    placeholder = 'Pick a date',
    required,
    disabled,
    className,
}: DateInputProps<T>) {
    const { watch, setValue, formState: { errors } } = form;
    const error = errors[name] as FieldError | undefined;
    const value = watch(name) as Date | undefined;

    return (
        <FormField
            name={name}
            label={label}
            description={description}
            error={error}
            required={required}
            className={className}
        >
            <Popover>
                <PopoverTrigger asChild>
                    <Button
                        variant="outline"
                        className={cn(
                            'w-full justify-start text-left font-normal',
                            !value && 'text-muted-foreground',
                            error && 'border-red-500'
                        )}
                        disabled={disabled}
                    >
                        <CalendarIcon className="mr-2 h-4 w-4" />
                        {value ? format(value, 'PPP') : placeholder}
                    </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0">
                    <Calendar
                        mode="single"
                        selected={value}
                        onSelect={(date) => setValue(name, date as T[typeof name])}
                        initialFocus
                    />
                </PopoverContent>
            </Popover>
        </FormField>
    );
}

interface FormProps<T extends FieldValues> {
    schema: z.ZodSchema<T>;
    defaultValues?: DefaultValues<T>;
    onSubmit: SubmitHandler<T>;
    children: (form: UseFormReturn<T>) => ReactNode;
    className?: string;
    resetOnSuccess?: boolean;
}

/**
 * Form wrapper with Zod validation
 */
export function Form<T extends FieldValues>({
    schema,
    defaultValues,
    onSubmit,
    children,
    className,
    resetOnSuccess = false,
}: FormProps<T>) {
    const form = useForm<T>({
        resolver: zodResolver(schema),
        defaultValues,
    });

    const handleSubmit = async (data: T) => {
        try {
            await onSubmit(data);
            if (resetOnSuccess) {
                form.reset();
            }
        } catch {
            // Errors are handled by the caller
        }
    };

    return (
        <form onSubmit={form.handleSubmit(handleSubmit)} className={className}>
            {children(form)}
        </form>
    );
}

interface SubmitButtonProps {
    isLoading?: boolean;
    disabled?: boolean;
    children?: ReactNode;
    className?: string;
}

/**
 * Submit button with loading state
 */
export function SubmitButton({
    isLoading,
    disabled,
    children = 'Submit',
    className,
}: SubmitButtonProps) {
    return (
        <Button type="submit" disabled={isLoading || disabled} className={className}>
            {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            {isLoading ? 'Saving...' : children}
        </Button>
    );
}

// Common validation schemas
export const schemas = {
    email: z.string().email('Please enter a valid email address'),
    password: z.string().min(8, 'Password must be at least 8 characters'),
    phone: z.string().regex(/^\+?[1-9]\d{1,14}$/, 'Please enter a valid phone number').optional(),
    url: z.string().url('Please enter a valid URL').optional(),
    required: (message = 'This field is required') => z.string().min(1, message),
    optionalString: z.string().optional(),
    positiveNumber: z.number().positive('Must be a positive number'),
    percentage: z.number().min(0).max(100, 'Must be between 0 and 100'),
    date: z.date({ required_error: 'Please select a date' }),
    optionalDate: z.date().optional(),
};

// Example form schema
export const leadFormSchema = z.object({
    firstName: z.string().min(1, 'First name is required'),
    lastName: z.string().min(1, 'Last name is required'),
    email: z.string().email('Invalid email address'),
    phone: z.string().optional(),
    company: z.string().optional(),
    jobTitle: z.string().optional(),
    status: z.string().min(1, 'Status is required'),
    source: z.string().optional(),
    notes: z.string().optional(),
});

export type LeadFormData = z.infer<typeof leadFormSchema>;

export const contactFormSchema = z.object({
    firstName: z.string().min(1, 'First name is required'),
    lastName: z.string().min(1, 'Last name is required'),
    email: z.string().email('Invalid email address'),
    phone: z.string().optional(),
    company: z.string().optional(),
    jobTitle: z.string().optional(),
    address: z.string().optional(),
    city: z.string().optional(),
    country: z.string().optional(),
    notes: z.string().optional(),
});

export type ContactFormData = z.infer<typeof contactFormSchema>;

export default {
    Form,
    FormField,
    TextInput,
    TextAreaInput,
    SelectInput,
    CheckboxInput,
    SwitchInput,
    DateInput,
    SubmitButton,
    schemas,
};
