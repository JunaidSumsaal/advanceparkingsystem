/* eslint-disable @typescript-eslint/no-explicit-any */
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
} from "@chakra-ui/react";
import { useEffect } from "react";

const Modals = ({ formData, isOpen, onClose, onSuccess, handleChange, handleSubmit, loading }: { formData: Record<string, any>, isOpen: boolean; onClose: () => void; onSuccess: boolean , handleChange: () => void, handleSubmit: () => void, loading: boolean  }) => {
  useEffect(() => {
    if(onSuccess) {
      onClose()
    }
  },[onClose, onSuccess])
  return (
    <Modal isOpen={isOpen} onClose={onClose} size="lg">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>Book</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <FormControl mb={4}>
            <FormLabel>Name</FormLabel>
            <Input name="name" value={formData.name} onChange={handleChange} />
          </FormControl>
          <FormControl mb={4}>
            <FormLabel>Amount</FormLabel>
            <Input name="amount" type="number" value={formData.location} onChange={handleChange} />
          </FormControl>
          <FormControl mb={4}>
            <FormLabel>Category</FormLabel>
            <Input name="category" value={formData.category} onChange={handleChange} />
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

export default Modals;
