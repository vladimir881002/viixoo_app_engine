import {
  Button,
  ButtonGroup,
  DialogActionTrigger,
  Select,
  createListCollection,
  Portal,
  Textarea,
  Box,
  Input,
} from "@chakra-ui/react"
import useCustomToast from "@/hooks/useCustomToast"
import { useState, useRef } from "react"
import { type SubmitHandler, useForm } from "react-hook-form"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { type ApiError, WorkOrdersService } from "@/client"
import { handleError } from "@/utils"

import type { WorkOrderPublic, BlockWorkOrder } from "../../client/types.gen"
import {
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTitle,
  DialogTrigger,
} from "../ui/dialog"
import { Field } from "../ui/field"


interface WorkOrderProps {
  item: WorkOrderPublic
}

export const blockRules = (isRequired = true) => {
  const rules: any = {}

  if (isRequired) {
    rules.required = "Campo obligatorio"
  }

  return rules
}

export const BlockWorkOrders = ({ item }: WorkOrderProps) => {
  const {
      handleSubmit,
      reset,
      register,
      formState: { isValid, isSubmitting },
    } = useForm<BlockWorkOrder>({
      mode: "onBlur",
      criteriaMode: "all",
    })
  const [isOpen, setIsOpen] = useState(false) 
  function getReasonsLossQueryOptions() {
    return {
      queryFn: () =>
        WorkOrdersService.readReasonsLoss(),
      queryKey: ["items"],
    }
  }
  const { data } = useQuery({
    ...getReasonsLossQueryOptions(),
    placeholderData: (prevData) => prevData,
  })
  const items_data = data?.data ?? []
  const reasons = createListCollection({items:items_data})
  const contentRef = useRef<HTMLDivElement>(null)
    
  const { showSuccessToast } = useCustomToast()
  const queryClient = useQueryClient() 
  const mutation = useMutation({
      mutationFn: (data: BlockWorkOrder) =>
        WorkOrdersService.blockWorkorder({ requestBody: data }),
      onSuccess: () => {
        showSuccessToast("Orden bloquada satisfactoriamente.")
        queryClient.invalidateQueries({ queryKey: ["items"] })
        reset()
      },
      onError: (err: ApiError) => {
        handleError(err)
      },
    })
  
    const onSubmit: SubmitHandler<BlockWorkOrder> = async (data) => {
      mutation.mutate(data)
    }
  return (
    <DialogRoot
      size={{ base: "xs", md: "md" }}
      placement="center"
      open={isOpen}
      onOpenChange={({ open }) => setIsOpen(open)}
    >
      <DialogTrigger asChild>
      <Button width="100%" variant="solid" size="md" colorPalette="red" display={
                  ['draft', 'done', 'cancel'].includes(item.production_state) || item.working_state == 'blocked'? 'none' : 'flex'
                }>Bloquear</Button>
      </DialogTrigger>
      <Portal>
      <DialogContent ref={contentRef}>
        <Box as="form" onSubmit={handleSubmit(onSubmit)}>
          <DialogHeader>
            <DialogTitle>Bloquear Orden de trabajo</DialogTitle>
          </DialogHeader>
          <DialogBody>
           <Field label="Motivo de pérdida:">
          <Select.Root required collection={reasons} size="sm" {...register("loss_id", blockRules())}>
            <Select.HiddenSelect />
            <Select.Control>
                  <Select.Trigger>
                    <Select.ValueText placeholder="Seleccione el motivo" />
                  </Select.Trigger>
                  <Select.IndicatorGroup>
                    <Select.Indicator />
                  </Select.IndicatorGroup>
                </Select.Control>
              <Portal container={contentRef}>
                  <Select.Positioner>
                    <Select.Content>
                      {reasons.items.map((item) => (
                        <Select.Item item={item} key={item.value}>
                          {item.label}
                        </Select.Item>
                      ))}
                    </Select.Content>
                  </Select.Positioner>
                </Portal>
              </Select.Root>
              </Field>
              <Field label="Descripción:">
              <Textarea {...register("description")}/>
              </Field>
              <Input value={item.workorder_id} display='none' {...register("workorder_id")}
                  />
          </DialogBody>

          <DialogFooter gap={2}>
            <ButtonGroup>
              <DialogActionTrigger asChild>
                <Button
                  colorPalette="red"
                  type="submit"
                  loading={isSubmitting}
                  disabled={!isValid}
                >
                  Bloquear
                </Button>
              </DialogActionTrigger>
              <DialogActionTrigger asChild>
                <Button
                  variant="subtle"
                  colorPalette="gray"
                >
                  Cerrar
                </Button>
              </DialogActionTrigger>
            </ButtonGroup>
          </DialogFooter>
        </Box>
        <DialogCloseTrigger />
      </DialogContent>
      </Portal>
    </DialogRoot>
  )
}
