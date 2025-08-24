export const formatSnakeCaseToTitleCase = (str: string): string => {
  // Ensure the input is a non-empty string before processing.
  if (typeof str !== 'string' || str.trim() === '') {
    return '';
  }

  return str
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};
