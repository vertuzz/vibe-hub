import { useState } from 'react';
import { dreamService } from '~/lib/services/dream-service';
import { useNavigate } from 'react-router-dom';

export default function CreateDream() {
    const [title, setTitle] = useState('');
    const [prompt, setPrompt] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const newDream = await dreamService.createDream({
                title,
                prompt_text: prompt,
                status: 'CONCEPT'
            });
            navigate(`/dreams/${newDream.id}`);
        } catch (err) {
            console.error(err);
        }
    };

    return (
        <div>
            <h1>Submit a Dream</h1>
            <form onSubmit={handleSubmit}>
                <div>
                    <label>Title</label>
                    <input value={title} onChange={(e) => setTitle(e.target.value)} required />
                </div>
                <div>
                    <label>Prompt</label>
                    <textarea value={prompt} onChange={(e) => setPrompt(e.target.value)} />
                </div>
                <button type="submit">Create Dream</button>
            </form>
        </div>
    );
}
