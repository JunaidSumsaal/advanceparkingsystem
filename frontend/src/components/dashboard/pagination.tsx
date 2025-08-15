import React from 'react';

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  handlePageChange: (page: number) => void;
}

const Pagination: React.FC<PaginationProps> = ({ currentPage, totalPages, handlePageChange }) => {
  const pageNumbers = Array.from({ length: totalPages }, (_, index) => index + 1); // Generate page numbers

  return (
    <nav aria-label="Page navigation example">
      <ul className="inline-flex -space-x-px text-sm">
        {/* Previous Button */}
        <li>
          <a 
            href="#"
            onClick={(e) => {
              e.preventDefault();
              if (currentPage > 1) {
                handlePageChange(currentPage - 1);
              }
            }}
            className={`flex items-center justify-center px-3 h-8 ms-0 leading-tight ${currentPage === 1 ? 'text-gray-300 cursor-not-allowed' : 'text-gray-500'} bg-white border border-e-0 border-gray-300 rounded-s-lg hover:bg-gray-100 hover:text-gray-700 dark:bg-gray-800 dark:border-gray-700 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-white`}
          >
            Previous
          </a>
        </li>
        
        {/* Page Number Buttons */}
        {pageNumbers.map((page) => (
          <li key={page}>
            <a 
              href="#"
              onClick={(e) => {
                e.preventDefault();
                handlePageChange(page);
              }}
              aria-current={currentPage === page ? "page" : undefined}
              className={`flex items-center justify-center px-3 h-8 leading-tight ${currentPage === page ? 'text-blue-600 border border-gray-300 bg-blue-50 hover:bg-blue-100 hover:text-blue-700 dark:border-gray-700 dark:bg-gray-700 dark:text-white' : 'text-gray-500 bg-white border border-gray-300 hover:bg-gray-100 hover:text-gray-700 dark:bg-gray-800 dark:border-gray-700 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-white'}`}
            >
              {page}
            </a>
          </li>
        ))}
        
        {/* Next Button */}
        <li>
          <a 
            href="#"
            onClick={(e) => {
              e.preventDefault();
              if (currentPage < totalPages) {
                handlePageChange(currentPage + 1);
              }
            }}
            className={`flex items-center justify-center px-3 h-8 leading-tight ${currentPage === totalPages ? 'text-gray-300 cursor-not-allowed' : 'text-gray-500'} bg-white border border-gray-300 rounded-e-lg hover:bg-gray-100 hover:text-gray-700 dark:bg-gray-800 dark:border-gray-700 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-white`}
          >
            Next
          </a>
        </li>
      </ul>
    </nav>
  );
};

export default Pagination;
