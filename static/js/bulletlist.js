const { useState, useImperativeHandle, forwardRef, useRef } = React;

const BulletList = forwardRef((props, ref) => {
    // Initialize with a default empty bullet point
    const [bulletPoints, setBulletPoints] = useState(['']);

    // Define component methods
    const addBulletPoint = () => {
        console.log("Adding bullet point");
        // Make sure we're properly updating the state array
        setBulletPoints(prevPoints => [...prevPoints, '']);
    };

    const removeBulletPoint = (index) => {
        console.log("Removing bullet point at index", index);
        // Use the functional form of setState to ensure we're using the latest state
        setBulletPoints(prevPoints => prevPoints.filter((_, i) => i !== index));
    };

    const updateBulletPoint = (index, value) => {
        console.log("Updating bullet point at index", index, "with value", value);
        // Use the functional form of setState
        setBulletPoints(prevPoints => {
            const newPoints = [...prevPoints];
            newPoints[index] = value;
            return newPoints;
        });
    };

    // Get the current bullet points
    const getBulletPoints = () => {
        console.log("Getting bullet points:", bulletPoints);
        return bulletPoints;
    };

    // Expose methods via useImperativeHandle
    useImperativeHandle(ref, () => ({
        addBulletPoint,
        removeBulletPoint,
        updateBulletPoint,
        getBulletPoints
    }));

    // Log when the component renders
    console.log("Rendering BulletList with points:", bulletPoints);

    return (
        <div className="bullet-list">
            <div className="bullet-items">
                {bulletPoints.map((bullet, index) => (
                    <div key={index} className="bullet-item">
                        <span className="bullet">•</span>
                        <input
                            type="text"
                            value={bullet}
                            onChange={(e) => updateBulletPoint(index, e.target.value)}
                            placeholder="Enter text here..."
                        />
                        {bulletPoints.length > 1 && (
                            <button
                                onClick={() => removeBulletPoint(index)}
                                className="remove-btn"
                            >
                                ×
                            </button>
                        )}
                    </div>
                ))}
            </div>
            <button 
                onClick={addBulletPoint}
                className="add-btn"
            >
                Add Bullet Point
            </button>
        </div>
    );
});