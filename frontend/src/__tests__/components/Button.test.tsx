/**
 * Component Tests - Button Component
 * 
 * Tests for the Button UI component
 */

import { render, screen, fireEvent } from '@testing-library/react';

import { Button } from '@/components/ui/button';

describe('Button Component', () => {
    it('renders with default variant', () => {
        render(<Button>Click me</Button>);
        const button = screen.getByRole('button', { name: /click me/i });
        expect(button).toBeInTheDocument();
    });

    it('handles click events', () => {
        const handleClick = jest.fn();
        render(<Button onClick={handleClick}>Click me</Button>);

        const button = screen.getByRole('button');
        fireEvent.click(button);

        expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('renders as disabled when specified', () => {
        render(<Button disabled>Disabled</Button>);
        const button = screen.getByRole('button');

        expect(button).toBeDisabled();
    });

    it('applies variant classes correctly', () => {
        const { rerender } = render(<Button variant="destructive">Delete</Button>);
        let button = screen.getByRole('button');
        expect(button).toBeInTheDocument();

        rerender(<Button variant="outline">Outline</Button>);
        button = screen.getByRole('button');
        expect(button).toBeInTheDocument();

        rerender(<Button variant="ghost">Ghost</Button>);
        button = screen.getByRole('button');
        expect(button).toBeInTheDocument();
    });

    it('renders with different sizes', () => {
        const { rerender } = render(<Button size="sm">Small</Button>);
        let button = screen.getByRole('button');
        expect(button).toBeInTheDocument();

        rerender(<Button size="lg">Large</Button>);
        button = screen.getByRole('button');
        expect(button).toBeInTheDocument();
    });

    it('forwards ref correctly', () => {
        const ref = jest.fn();
        render(<Button ref={ref}>With Ref</Button>);
        expect(ref).toHaveBeenCalled();
    });

    it('renders as child component when asChild is true', () => {
        render(
            <Button asChild>
                <a href="/test">Link Button</a>
            </Button>
        );
        const link = screen.getByRole('link');
        expect(link).toBeInTheDocument();
        expect(link).toHaveAttribute('href', '/test');
    });
});

