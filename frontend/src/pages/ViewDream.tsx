import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { dreamService } from '~/lib/services/dream-service';
import type { Dream } from '~/lib/types';

export default function ViewDream() {
    const { id } = useParams<{ id: string }>();
    const [dream, setDream] = useState<Dream | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (id) {
            dreamService.getDream(parseInt(id)).then((data) => {
                setDream(data);
                setLoading(false);
            }).catch(err => {
                console.error(err);
                setLoading(false);
            });
        }
    }, [id]);

    if (loading) return <div>Loading dream...</div>;
    if (!dream) return <div>Dream not found</div>;

    return (
        <div>
            <h1>{dream.title}</h1>
            <p>Status: {dream.status}</p>
            <div>
                <h3>Prompt</h3>
                <p>{dream.prompt_text}</p>
            </div>
            {dream.app_url && (
                <a href={dream.app_url} target="_blank" rel="noopener noreferrer">Try it now</a>
            )}
        </div>
    );
}
