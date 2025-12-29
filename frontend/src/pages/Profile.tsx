import { useEffect, useState } from 'react';
import { authService } from '~/lib/services/auth-service';
import type { User } from '~/lib/types';

export default function Profile() {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        authService.getMe().then((data) => {
            setUser(data);
            setLoading(false);
        }).catch(err => {
            console.error(err);
            setLoading(false);
        });
    }, []);

    if (loading) return <div>Loading profile...</div>;
    if (!user) return <div>Please login to view your profile</div>;

    return (
        <div>
            <h1>Profile</h1>
            <p>Username: {user.username}</p>
            <p>Email: {user.email}</p>
            <button onClick={() => { authService.logout(); window.location.href = '/login'; }}>Logout</button>
        </div>
    );
}
