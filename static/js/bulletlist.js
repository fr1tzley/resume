import React, { useState } from 'react';

function BulletList() {
    const [bulletPoints, setBulletPoints] = useState(['']);

    const addBulletPoint = () => {
        setBulletPoints([...bulletPoints, '']);
    };

    const removeBulletPoint = (index) => {
        const newBulletPoints = bulletPoints.filter((_, i) => i !== index);
        setBulletPoints(newBulletPoints);
    };

    const updateBulletPoint = (index, value) => {
        const newBulletPoints = [...bulletPoints];
        newBulletPoints[index] = value;
        setBulletPoints(newBulletPoints);
    };

    return (
        <div className="bullet-list p-4">
            <div className="bullet-items space-y-2">
                {bulletPoints.map((bullet, index) => (
                    <div key={index} className="bullet-item flex items-center gap-2">
                        <span className="bullet text-xl">•</span>
                        <input
                            type="text"
                            value={bullet}
                            onChange={(e) => updateBulletPoint(index, e.target.value)}
                            placeholder="Enter text here..."
                            className="flex-1 px-2 py-1 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                        {bulletPoints.length > 1 && (
                            <button
                                onClick={() => removeBulletPoint(index)}
                                className="delete-btn p-1 text-gray-500 hover:text-red-500 transition-colors"
                                aria-label="Delete bullet point"
                            >
                            </button>
                        )}
                    </div>
                ))}
            </div>
            <button 
                onClick={addBulletPoint}
                className="add-btn mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
            >
                Add Bullet Point
            </button>
        </div>
    );
}
