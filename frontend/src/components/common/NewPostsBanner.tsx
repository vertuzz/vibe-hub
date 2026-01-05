interface NewPostsBannerProps {
    onRefresh: () => void;
}

export default function NewPostsBanner({ onRefresh }: NewPostsBannerProps) {
    return (
        <button
            onClick={onRefresh}
            className="fixed top-20 left-1/2 -translate-x-1/2 z-50 
                       bg-primary hover:bg-primary-dark text-white 
                       px-4 py-2 rounded-full shadow-lg 
                       flex items-center gap-2 
                       animate-fade-in-up hover:animate-bounce-subtle
                       transition-colors duration-200
                       text-sm font-medium"
        >
            <span className="material-symbols-outlined text-[18px]">arrow_upward</span>
            New posts available
        </button>
    );
}
