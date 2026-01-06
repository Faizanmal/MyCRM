// Mock for lucide-react icons
import React from 'react';

const createIcon = (name: string) => {
    const Icon = React.forwardRef<SVGSVGElement, React.SVGProps<SVGSVGElement>>(
        (props, ref) => (
            <svg ref={ref} data-testid={`icon-${name}`} {...props}>
                <title>{name}</title>
            </svg>
        )
    );
    Icon.displayName = name;
    return Icon;
};

// Export commonly used icons
export const AlertTriangle = createIcon('AlertTriangle');
export const ArrowDown = createIcon('ArrowDown');
export const ArrowUp = createIcon('ArrowUp');
export const BarChart3 = createIcon('BarChart3');
export const Bell = createIcon('Bell');
export const Building2 = createIcon('Building2');
export const Calendar = createIcon('Calendar');
export const Check = createIcon('Check');
export const CheckCircle = createIcon('CheckCircle');
export const CheckCircle2 = createIcon('CheckCircle2');
export const ChevronDown = createIcon('ChevronDown');
export const ChevronLeft = createIcon('ChevronLeft');
export const ChevronRight = createIcon('ChevronRight');
export const ChevronUp = createIcon('ChevronUp');
export const Clock = createIcon('Clock');
export const Copy = createIcon('Copy');
export const Database = createIcon('Database');
export const Download = createIcon('Download');
export const Edit = createIcon('Edit');
export const Eye = createIcon('Eye');
export const EyeOff = createIcon('EyeOff');
export const Filter = createIcon('Filter');
export const Home = createIcon('Home');
export const Linkedin = createIcon('Linkedin');
export const Loader2 = createIcon('Loader2');
export const LogOut = createIcon('LogOut');
export const Mail = createIcon('Mail');
export const Menu = createIcon('Menu');
export const MoreHorizontal = createIcon('MoreHorizontal');
export const MoreVertical = createIcon('MoreVertical');
export const Pause = createIcon('Pause');
export const Play = createIcon('Play');
export const Plus = createIcon('Plus');
export const RefreshCw = createIcon('RefreshCw');
export const Search = createIcon('Search');
export const Settings = createIcon('Settings');
export const Sparkles = createIcon('Sparkles');
export const Star = createIcon('Star');
export const Target = createIcon('Target');
export const Trash = createIcon('Trash');
export const Trash2 = createIcon('Trash2');
export const TrendingUp = createIcon('TrendingUp');
export const TrendingDown = createIcon('TrendingDown');
export const Upload = createIcon('Upload');
export const User = createIcon('User');
export const Users = createIcon('Users');
export const X = createIcon('X');
export const Zap = createIcon('Zap');

// Default export for icons that might be imported differently
const lucideReactMock = {
    AlertTriangle,
    ArrowDown,
    ArrowUp,
    BarChart3,
    Bell,
    Building2,
    Calendar,
    Check,
    CheckCircle,
    CheckCircle2,
    ChevronDown,
    ChevronLeft,
    ChevronRight,
    ChevronUp,
    Clock,
    Copy,
    Database,
    Download,
    Edit,
    Eye,
    EyeOff,
    Filter,
    Home,
    Linkedin,
    Loader2,
    LogOut,
    Mail,
    Menu,
    MoreHorizontal,
    MoreVertical,
    Pause,
    Play,
    Plus,
    RefreshCw,
    Search,
    Settings,
    Sparkles,
    Star,
    Target,
    Trash,
    Trash2,
    TrendingUp,
    TrendingDown,
    Upload,
    User,
    Users,
    X,
    Zap,
};

export default lucideReactMock;
