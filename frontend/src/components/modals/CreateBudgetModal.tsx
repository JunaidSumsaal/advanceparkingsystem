import {
  Button,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  FormControl,
  FormLabel,
  Input,
  useToast,
} from "@chakra-ui/react";
import { useState } from "react";
import { createBudget } from "../../services/budgetService";

const CreateBudgetModal = ({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) => {
  const [formData, setFormData] = useState({
    name: '',
    amount: '',
    category: '',
    month: '',
  });
  const [loading, setLoading] = useState(false);
  const toast = useToast();

  const handleChange = (e: any) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      let monthFormatted = '';

    if (formData.month) {
      const selectedDate = new Date(formData.month);
      // monthFormatted = format(selectedDate, 'yyyy-MM'); 
      monthFormatted = `${selectedDate.getFullYear()}-${String(selectedDate.getMonth() + 1).padStart(2, '0')}`;
    }

      const payload = {
        name: formData.name,
        amount: formData.amount,
        category: formData.category,
        month: monthFormatted,
      };
      await createBudget(payload);
      toast({
        title: "Budget created!",
        status: "success",
        duration: 3000,
        isClosable: true,
      });
      onClose();
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.message || "Something went wrong.",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="lg">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>Add New Budget</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <FormControl mb={4}>
            <FormLabel>Name</FormLabel>
            <Input name="name" value={formData.name} onChange={handleChange} />
          </FormControl>
          <FormControl mb={4}>
            <FormLabel>Amount</FormLabel>
            <Input name="amount" type="number" value={formData.amount} onChange={handleChange} />
          </FormControl>
          <FormControl mb={4}>
            <FormLabel>Category</FormLabel>
            <Input name="category" value={formData.category} onChange={handleChange} />
          </FormControl>
          <FormControl mb={4}>
            <FormLabel>Month</FormLabel>
            <Input 
              name="month" 
              type="date" 
              value={formData.month} 
              onChange={handleChange} 
            />
          </FormControl>
        </ModalBody>

        <ModalFooter>
          <Button bg="primary.400" color="white" mr={3} onClick={handleSubmit} isLoading={loading}>
            Save
          </Button>
          <Button variant="ghost" onClick={onClose}>Cancel</Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

export default CreateBudgetModal;
