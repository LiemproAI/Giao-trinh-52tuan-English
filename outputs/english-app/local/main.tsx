import React from 'react';
import {createRoot} from 'react-dom/client';
import Garden from '../app/garden';
import '../app/design.css';
createRoot(document.getElementById('root')!).render(<Garden localMode/>);

