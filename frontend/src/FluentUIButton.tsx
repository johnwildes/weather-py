import { DefaultButton } from '@fluentui/react';

function FluentUIButton() {
    return (
        <div style={{ margin: '20px' }}>
            <DefaultButton text="Click Me" onClick={() => alert('FluentUI Button Clicked!')} />
        </div>
    );
}

export default FluentUIButton;