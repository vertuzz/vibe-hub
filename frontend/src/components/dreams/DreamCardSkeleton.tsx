// Skeleton loader for Dream cards
export default function DreamCardSkeleton() {
  return (
    <div className="break-inside-avoid mb-6">
      <div className="bg-white dark:bg-gray-800 rounded-2xl overflow-hidden shadow-sm border border-gray-100 dark:border-gray-700">
        {/* Image Skeleton */}
        <div className="relative aspect-[4/3] w-full overflow-hidden bg-gray-200 dark:bg-gray-700 animate-pulse" />

        {/* Content Skeleton */}
        <div className="p-4 space-y-3">
          {/* Title */}
          <div className="h-5 bg-gray-200 dark:bg-gray-700 rounded animate-pulse w-3/4" />
          
          {/* Description */}
          <div className="space-y-2">
            <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
            <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded animate-pulse w-2/3" />
          </div>

          {/* Footer */}
          <div className="flex items-center justify-between border-t border-gray-100 dark:border-gray-700 pt-3 mt-2">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-full bg-gray-200 dark:bg-gray-700 animate-pulse" />
              <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded animate-pulse w-16" />
            </div>
            <div className="flex items-center gap-3">
              <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded animate-pulse w-8" />
              <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded animate-pulse w-8" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
