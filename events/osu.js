import { spawn } from 'child_process';
import path from 'path';

export function register(app) {
    const pythonPath = path.resolve('./events/osuSlack.py');

    const python = spawn('python3', [pythonPath]);

    python.stdout.on('data', (data) => {
        console.log(`[osu.py] ${data.toString().trim()}`);
    });

    python.stderr.on('data', (data) => {
        console.error(`[osu.py error] ${data.toString().trim()}`);
    });

    python.on('close', (code) => {
        console.log(`[osu.py] process exited with code ${code}`);
    });
}