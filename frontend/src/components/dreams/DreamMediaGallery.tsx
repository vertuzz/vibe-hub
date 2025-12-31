import { useState } from 'react';
import type { DreamMedia } from '~/lib/types';

interface DreamMediaGalleryProps {
    media?: DreamMedia[];
    youtubeUrl?: string;
    title: string;
}

// Helper to extract YouTube video ID
function getYouTubeVideoId(url: string): string | null {
    const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/;
    const match = url.match(regExp);
    return match && match[2].length === 11 ? match[2] : null;
}

export default function DreamMediaGallery({ media, youtubeUrl, title }: DreamMediaGalleryProps) {
    const [selectedMediaIndex, setSelectedMediaIndex] = useState(0);

    const hasYouTube = youtubeUrl && getYouTubeVideoId(youtubeUrl);
    const heroMedia = media && media.length > 0 ? media[selectedMediaIndex]?.media_url : null;
    const youtubeId = youtubeUrl ? getYouTubeVideoId(youtubeUrl) : null;

    return (
        <section className="flex flex-col gap-4">
            {/* Main Preview (Hero) */}
            <div className="relative w-full aspect-[3/2] rounded-2xl overflow-hidden bg-gray-900 shadow-sm group">
                {hasYouTube && selectedMediaIndex === -1 ? (
                    <iframe
                        className="absolute inset-0 w-full h-full"
                        src={`https://www.youtube.com/embed/${youtubeId}`}
                        title={title}
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                        allowFullScreen
                    />
                ) : heroMedia ? (
                    <>
                        {/* Blurred background for premium feel and to fill gaps */}
                        <div
                            className="absolute inset-0 bg-cover bg-center blur-2xl opacity-50 scale-110 pointer-events-none"
                            style={{ backgroundImage: `url('${heroMedia}')` }}
                        />
                        <div className="absolute inset-0 bg-black/10" />

                        {/* Main image - contain to avoid cropping */}
                        <img
                            src={heroMedia}
                            alt={title}
                            className="relative z-10 w-full h-full object-contain transition-transform duration-700 group-hover:scale-[1.02]"
                        />
                    </>
                ) : hasYouTube ? (
                    <>
                        <div
                            className="absolute inset-0 bg-cover bg-center transition-transform duration-700 group-hover:scale-105"
                            style={{ backgroundImage: `url('https://img.youtube.com/vi/${youtubeId}/maxresdefault.jpg')` }}
                        />
                        <div className="absolute inset-0 bg-black/40 group-hover:bg-black/30 transition-colors" />
                        <button
                            onClick={() => setSelectedMediaIndex(-1)}
                            className="absolute inset-0 m-auto size-20 flex items-center justify-center rounded-full bg-white/20 backdrop-blur-sm text-white hover:bg-white/30 hover:scale-110 transition-all duration-300 z-20"
                        >
                            <span className="material-symbols-outlined text-5xl filled">play_arrow</span>
                        </button>
                    </>
                ) : (
                    <img
                        src="/placeholder-dream.png"
                        alt={title}
                        className="w-full h-full object-cover"
                    />
                )}
            </div>

            {/* Thumbnails Carousel */}
            {((media && media.length > 0) || hasYouTube) && (
                <div className="flex gap-3 overflow-x-auto pb-2 scrollbar-hide snap-x">
                    {hasYouTube && (
                        <button
                            onClick={() => setSelectedMediaIndex(-1)}
                            className={`relative shrink-0 w-32 aspect-[3/2] rounded-lg overflow-hidden snap-start ${selectedMediaIndex === -1
                                ? 'ring-2 ring-primary ring-offset-2 ring-offset-[var(--background)]'
                                : 'border border-[var(--border)] opacity-70 hover:opacity-100'
                                } transition-opacity`}
                        >
                            <img
                                className="w-full h-full object-cover"
                                src={`https://img.youtube.com/vi/${youtubeId}/mqdefault.jpg`}
                                alt="YouTube video"
                            />
                            <div className="absolute inset-0 flex items-center justify-center bg-black/30">
                                <span className="material-symbols-outlined text-white text-2xl filled">play_arrow</span>
                            </div>
                        </button>
                    )}
                    {media?.map((item, index) => (
                        <button
                            key={item.id}
                            onClick={() => setSelectedMediaIndex(index)}
                            className={`relative shrink-0 w-32 aspect-[3/2] rounded-lg overflow-hidden snap-start ${selectedMediaIndex === index
                                ? 'ring-2 ring-primary ring-offset-2 ring-offset-[var(--background)]'
                                : 'border border-[var(--border)] opacity-70 hover:opacity-100'
                                } transition-opacity`}
                        >
                            <img
                                className="w-full h-full object-cover"
                                src={item.media_url}
                                alt={`Screenshot ${index + 1}`}
                            />
                        </button>
                    ))}
                </div>
            )}
        </section>
    );
}
