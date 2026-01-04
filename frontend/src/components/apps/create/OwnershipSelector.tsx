import React from 'react';

interface OwnershipSelectorProps {
    isOwner: boolean;
    onChange: (isOwner: boolean) => void;
}

const OwnershipSelector: React.FC<OwnershipSelectorProps> = ({ isOwner, onChange }) => {
    return (
        <div className="space-y-4 p-4 rounded-xl bg-slate-50/50 border border-slate-100">
            <h3 className="text-sm font-semibold text-slate-900">Ownership</h3>
            <p className="text-xs text-slate-500">Are you the creator of this app?</p>

            <div className="flex flex-col space-y-3">
                <label className="flex items-center space-x-3 cursor-pointer group">
                    <div className="relative flex items-center justify-center">
                        <input
                            type="radio"
                            className="peer appearance-none w-5 h-5 rounded-full border-2 border-slate-300 checked:border-indigo-600 transition-all"
                            name="ownership"
                            checked={isOwner}
                            onChange={() => onChange(true)}
                        />
                        <div className="absolute w-2.5 h-2.5 rounded-full bg-indigo-600 opacity-0 peer-checked:opacity-100 transition-all" />
                    </div>
                    <span className="text-sm text-slate-700 group-hover:text-slate-900 transition-colors">
                        Yes, I built this app
                    </span>
                </label>

                <label className="flex items-center space-x-3 cursor-pointer group">
                    <div className="relative flex items-center justify-center">
                        <input
                            type="radio"
                            className="peer appearance-none w-5 h-5 rounded-full border-2 border-slate-300 checked:border-indigo-600 transition-all"
                            name="ownership"
                            checked={!isOwner}
                            onChange={() => onChange(false)}
                        />
                        <div className="absolute w-2.5 h-2.5 rounded-full bg-indigo-600 opacity-0 peer-checked:opacity-100 transition-all" />
                    </div>
                    <span className="text-sm text-slate-700 group-hover:text-slate-900 transition-colors">
                        No, I'm submitting on behalf of someone else
                    </span>
                </label>
            </div>

            {!isOwner && (
                <p className="text-[10px] text-slate-400 mt-2 bg-white/50 p-2 rounded-lg italic">
                    Note: If you are the real owner but someone else submitted your app, you can claim ownership later from the app page.
                </p>
            )}
        </div>
    );
};

export default OwnershipSelector;
