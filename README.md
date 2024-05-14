# sample_demo
practiceimport axios from 'axios';
import fs from 'fs';

const apiKey = 'YOUR_FIGMA_API_KEY';
const fileId = 'YOUR_FILE_ID';
const url = `https://api.figma.com/v1/files/${fileId}`;

axios.get(url, {
  headers: { 'X-Figma-Token': apiKey }
})
  .then(response => {
    fs.writeFileSync('figma.json', JSON.stringify(response.data, null, 2));
  })
  .catch(error => console.error('Error fetching Figma file:', error));











testimport fs from 'fs';

const figmaData = JSON.parse(fs.readFileSync('figma.json', 'utf8'));

const figmaColorToCSS = (color: { r: number, g: number, b: number, a: number }): string => {
  const r = Math.round(color.r * 255);
  const g = Math.round(color.g * 255);
  const b = Math.round(color.b * 255);
  const a = color.a;
  return `rgba(${r}, ${g}, ${b}, ${a})`;
};

const figmaNodeToMui = (node: any): string => {
  switch (node.type) {
    case 'FRAME':
    case 'GROUP':
      return `
        import React from 'react';
        import { Box } from '@mui/material';

        const ${node.name.replace(/\s+/g, '')} = () => (
          <Box style={{
            position: 'absolute',
            top: ${node.absoluteBoundingBox.y}px,
            left: ${node.absoluteBoundingBox.x}px,
            width: ${node.absoluteBoundingBox.width}px,
            height: ${node.absoluteBoundingBox.height}px,
            ${node.background ? `background: ${figmaColorToCSS(node.background[0].color)};` : ''}
          }}>
            ${node.children ? node.children.map((child: any) => figmaNodeToMui(child)).join('\n') : ''}
          </Box>
        );

        export default ${node.name.replace(/\s+/g, '')};
      `;
    case 'TEXT':
      return `
        import React from 'react';
        import { Typography } from '@mui/material';

        const ${node.name.replace(/\s+/g, '')} = () => (
          <Typography style={{
            position: 'absolute',
            top: ${node.absoluteBoundingBox.y}px,
            left: ${node.absoluteBoundingBox.x}px,
            fontSize: ${node.style.fontSize}px,
            fontWeight: ${node.style.fontWeight},
            color: '${figmaColorToCSS(node.fills[0].color)}',
            fontFamily: '${node.style.fontFamily}',
            lineHeight: '${node.style.lineHeight}px',
          }}>
            ${node.characters}
          </Typography>
        );

        export default ${node.name.replace(/\s+/g, '')};
      `;
    case 'RECTANGLE':
      return `
        import React from 'react';
        import { Box } from '@mui/material';

        const ${node.name.replace(/\s+/g, '')} = () => (
          <Box style={{
            position: 'absolute',
            top: ${node.absoluteBoundingBox.y}px,
            left: ${node.absoluteBoundingBox.x}px,
            width: ${node.absoluteBoundingBox.width}px,
            height: ${node.absoluteBoundingBox.height}px,
            backgroundColor: '${figmaColorToCSS(node.fills[0].color)}',
            borderRadius: '${node.cornerRadius}px'
          }} />
        );

        export default ${node.name.replace(/\s+/g, '')};
      `;
    // Add cases for other node types as needed
    default:
      return '';
  }
};

const generateMuiComponents = (node: any): void => {
  const componentCode = figmaNodeToMui(node);
  const componentName = node.name.replace(/\s+/g, '');
  fs.writeFileSync(`${componentName}.tsx`, componentCode);

  if (node.children) {
    node.children.forEach((child: any) => generateMuiComponents(child));
  }
};

generateMuiComponents(figmaData.document);

console.log('MUI components have been generated.');




