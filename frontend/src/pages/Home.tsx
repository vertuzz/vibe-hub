import { useEffect, useState } from 'react';
import { dreamService } from '~/lib/services/dream-service';
import type { Dream } from '~/lib/types';
import { Link } from 'react-router-dom';

export default function Home() {
    const [dreams, setDreams] = useState<Dream[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        dreamService.getDreams().then((data) => {
            setDreams(data);
            setLoading(false);
        }).catch(err => {
            console.error(err);
            setLoading(false);
        });
    }, []);

    if (loading) return <div>Loading dreams...</div>;

    return (
        <div>
            <h1>Dreamware Feed</h1>
            <Link to="/dreams/create">Submit a Dream</Link>
            <div className="dream-list">
                {dreams.map((dream) => (
                    <div key={dream.id} className="dream-card">
                        <h2>{dream.title}</h2>
                        <p>{dream.prompt_text ? dream.prompt_text.substring(0, 100) + '...' : 'No description'}</p>
                        <Link to={`/dreams/${dream.id}`}>View Details</Link>
                    </div>
                ))}
            </div>
        </div>
    );
}
