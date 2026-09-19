import { ReceiptApi } from '../../api/receiptApi';
import { fetchApi } from '../../api/client';

export const fastapiReceiptApi: ReceiptApi = {
  uploadReceipt: async (file: File) => {
    // Note: FormData requires custom handling bypassing the default JSON content-type
    // For now we leave this as a stub since it's multipart
    return [];
  }
};
